import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from appworld.common.path_store import path_store
from appworld.serve import environment
from appworld.serve.experiment_status import ExperimentStatus


@pytest.fixture
def experiment_root(tmp_path, monkeypatch):
    monkeypatch.setenv("APPWORLD_ROOT", str(tmp_path))
    path_store.reload()
    outputs = tmp_path / "experiments" / "outputs"
    outputs.mkdir(parents=True)
    return outputs


@pytest.fixture
def experiment_status():
    return ExperimentStatus()


def _write_report(task_dir: str, passed: int, failed: int, total: int) -> None:
    eval_dir = os.path.join(task_dir, "evaluation")
    os.makedirs(eval_dir, exist_ok=True)
    with open(os.path.join(eval_dir, "report.md"), "w", encoding="utf-8") as handle:
        handle.write(
            f"Num Passed Tests : {passed}\n"
            f"Num Failed Tests : {failed}\n"
            f"Num Total Tests : {total}\n"
        )


def _touch_finished(task_dir: str) -> None:
    misc_dir = os.path.join(task_dir, "misc")
    os.makedirs(misc_dir, exist_ok=True)
    with open(os.path.join(misc_dir, "finished"), "w", encoding="utf-8") as handle:
        handle.write("done\n")


class TestExperimentStatus:
    def test_list_experiments(self, experiment_root) -> None:
        for name in ("alpha", "beta"):
            (experiment_root / name).mkdir()
        (experiment_root / ".hidden").mkdir()

        assert ExperimentStatus().list_experiments() == ["alpha", "beta"]

    def test_status_not_started(self, experiment_root, experiment_status) -> None:
        (experiment_root / "test_exp" / "tasks").mkdir(parents=True)

        with patch.object(ExperimentStatus, "_load_instruction", return_value="do something"):
            row = experiment_status._task_status_row("test_exp", "task_a", is_active=False)

        assert row.status == "not_started"
        assert row.has_output is False
        assert row.agent_finished is False

    def test_status_in_progress(self, experiment_root, experiment_status) -> None:
        task_dir = experiment_root / "test_exp" / "tasks" / "task_b"
        task_dir.mkdir(parents=True)

        with patch.object(ExperimentStatus, "_load_instruction", return_value="in progress"):
            row = experiment_status._task_status_row("test_exp", "task_b", is_active=False)

        assert row.status == "in_progress"
        assert row.has_output is True

    def test_status_finished(self, experiment_root, experiment_status) -> None:
        task_dir = experiment_root / "test_exp" / "tasks" / "task_c"
        task_dir.mkdir(parents=True)
        _touch_finished(str(task_dir))

        with patch.object(ExperimentStatus, "_load_instruction", return_value="finished"):
            row = experiment_status._task_status_row("test_exp", "task_c", is_active=False)

        assert row.status == "finished"
        assert row.agent_finished is True

    def test_status_pass_and_fail(self, experiment_root, experiment_status) -> None:
        pass_dir = experiment_root / "test_exp" / "tasks" / "task_pass"
        fail_dir = experiment_root / "test_exp" / "tasks" / "task_fail"
        pass_dir.mkdir(parents=True)
        fail_dir.mkdir(parents=True)
        _write_report(str(pass_dir), passed=3, failed=0, total=3)
        _write_report(str(fail_dir), passed=1, failed=2, total=3)

        with patch.object(ExperimentStatus, "_load_instruction", return_value="evaluated"):
            pass_row = experiment_status._task_status_row("test_exp", "task_pass", is_active=False)
            fail_row = experiment_status._task_status_row("test_exp", "task_fail", is_active=False)

        assert pass_row.status == "pass"
        assert pass_row.pass_percentage == 100.0
        assert fail_row.status == "fail"
        assert fail_row.pass_percentage == pytest.approx(33.3)

    def test_status_active_overlay(self, experiment_root, experiment_status) -> None:
        task_dir = experiment_root / "test_exp" / "tasks" / "task_live"
        task_dir.mkdir(parents=True)

        with patch.object(ExperimentStatus, "_load_instruction", return_value="live"):
            row = experiment_status._task_status_row("test_exp", "task_live", is_active=True)

        assert row.status == "active"
        assert row.is_active is True

    def test_task_status_cache(self, experiment_root, experiment_status) -> None:
        tasks_root = experiment_root / "test_exp" / "tasks"
        tasks_root.mkdir(parents=True)
        (tasks_root / "cached_task").mkdir()

        with patch.object(ExperimentStatus, "_load_instruction", return_value="cached"):
            first = experiment_status.task_status_for_experiment("test_exp")
            second = experiment_status.task_status_for_experiment("test_exp")

        assert first is second
        assert first["task_count"] == 1

    def test_task_progress_from_api_calls_log(self, experiment_root, experiment_status) -> None:
        task_dir = experiment_root / "test_exp" / "tasks" / "task_prog"
        logs_dir = task_dir / "logs"
        logs_dir.mkdir(parents=True)
        api_log = logs_dir / "api_calls.jsonl"
        api_log.write_text(
            '{"method": "get", "url": "/phone/messages", "data": {}}\n'
            '{"method": "post", "url": "/simple_note/notes", "data": {}}\n',
            encoding="utf-8",
        )

        progress = experiment_status._task_progress("test_exp", "task_prog")

        assert progress is not None
        assert progress["api_call_count"] == 2
        assert progress["current_step"] == "POST simple_note.notes"
        assert progress["apps_touched"] == ["phone", "simple_note"]
        assert len(progress["last_api_calls"]) == 2
    @pytest.fixture
    def client(self):
        return TestClient(environment.app)

    @pytest.fixture(autouse=True)
    def reset_world(self):
        environment.world = None
        yield
        environment.world = None

    def test_list_experiments_endpoint(self, client, experiment_root) -> None:
        (experiment_root / "api_exp").mkdir()

        response = client.get("/experiments")

        assert response.status_code == 200
        assert response.json()["output"] == ["api_exp"]

    def test_active_status_none(self, client) -> None:
        response = client.get("/status/active")

        assert response.status_code == 200
        assert response.json()["output"] is None

    def test_active_status_with_world(self, client) -> None:
        mock_world = MagicMock()
        mock_world.task_id = "live_task_1"
        mock_world.experiment_name = "api_exp"
        mock_world.task.id = "live_task_1"
        mock_world.task.instruction = "complete the task"
        mock_world.task.datetime = "2024-01-01T00:00:00"
        mock_world.task_completed.return_value = True
        environment.world = mock_world

        response = client.get("/status/active")

        assert response.status_code == 200
        payload = response.json()["output"]
        assert payload["task_id"] == "live_task_1"
        assert payload["task_completed"] is True
        assert payload["experiment_name"] == "api_exp"

    def test_task_status_endpoint(self, client, experiment_root) -> None:
        task_dir = experiment_root / "route_exp" / "tasks" / "route_task"
        task_dir.mkdir(parents=True)
        _write_report(str(task_dir), passed=2, failed=0, total=2)

        with patch.object(ExperimentStatus, "_load_instruction", return_value="route task"):
            response = client.get("/experiments/route_exp/tasks/status?task_ids=route_task")

        assert response.status_code == 200
        payload = response.json()["output"]
        assert payload["experiment_name"] == "route_exp"
        assert payload["task_count"] == 1
        assert payload["tasks"][0]["status"] == "pass"

    def test_task_status_marks_active_task(self, client, experiment_root) -> None:
        task_dir = experiment_root / "route_exp" / "tasks" / "active_task"
        task_dir.mkdir(parents=True)

        mock_world = MagicMock()
        mock_world.task_id = "active_task"
        environment.world = mock_world

        with patch.object(ExperimentStatus, "_load_instruction", return_value="active"):
            response = client.get("/experiments/route_exp/tasks/status?task_ids=active_task")

        task = response.json()["output"]["tasks"][0]
        assert task["is_active"] is True
        assert task["status"] == "active"
        assert response.json()["output"]["active_task_id"] == "active_task"

    def test_evaluate_endpoint(self, client, monkeypatch) -> None:
        mock_tracker = MagicMock()
        mock_tracker.to_dict.return_value = {"pass_count": 1}
        monkeypatch.setattr(environment, "evaluate_task", lambda **_: mock_tracker)

        response = client.post("/experiments/eval_exp/tasks/task_x/evaluate")

        assert response.status_code == 200
        assert response.json()["output"] == {"pass_count": 1}

    def test_dashboard_endpoint(self, client) -> None:
        response = client.get("/dashboard")

        assert response.status_code == 200
        assert "Experiment Dashboard" in response.text
