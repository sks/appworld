"""Scan experiment outputs and derive per-task run status for the dashboard."""
from __future__ import annotations

import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from appworld.common.path_store import path_store
from appworld.environment import AppWorld
from appworld.task import Task, load_task_ids


_CACHE_TTL_SECONDS = 3.0
_status_cache: dict[str, tuple[float, dict[str, Any]]] = {}


@dataclass
class TaskStatusRow:
    task_id: str
    status: str
    is_active: bool
    instruction: str | None
    pass_percentage: float | None
    pass_count: int | None
    fail_count: int | None
    num_tests: int | None
    evaluated_at: str | None
    has_output: bool
    agent_finished: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExperimentStatus:
    """Reads experiment output directories and summarizes task run status."""

    def list_experiments(self) -> list[str]:
        outputs_root = path_store.experiment_outputs
        if not os.path.isdir(outputs_root):
            return []
        names = [
            name
            for name in os.listdir(outputs_root)
            if os.path.isdir(os.path.join(outputs_root, name)) and not name.startswith(".")
        ]
        return sorted(names)

    def resolve_task_ids(
        self,
        experiment_name: str,
        task_ids: list[str] | None = None,
        dataset: str | None = None,
    ) -> list[str]:
        resolved: set[str] = set()
        if task_ids:
            resolved.update(task_ids)
        if dataset:
            resolved.update(load_task_ids(dataset))
        tasks_root = self._tasks_root(experiment_name)
        if os.path.isdir(tasks_root):
            for name in os.listdir(tasks_root):
                task_dir = os.path.join(tasks_root, name)
                if os.path.isdir(task_dir):
                    resolved.add(name)
        return sorted(resolved)

    def task_status_for_experiment(
        self,
        experiment_name: str,
        *,
        task_ids: list[str] | None = None,
        dataset: str | None = None,
        active_task_id: str | None = None,
    ) -> dict[str, Any]:
        cache_key = f"{experiment_name}|{task_ids}|{dataset}|{active_task_id}"
        cached = _status_cache.get(cache_key)
        now = time.time()
        if cached is not None and now - cached[0] < _CACHE_TTL_SECONDS:
            return cached[1]

        ids = self.resolve_task_ids(experiment_name, task_ids=task_ids, dataset=dataset)
        rows = [
            self._task_status_row(
                experiment_name,
                task_id,
                is_active=active_task_id is not None and task_id == active_task_id,
            )
            for task_id in ids
        ]
        output = {
            "experiment_name": experiment_name,
            "active_task_id": active_task_id,
            "task_count": len(rows),
            "tasks": [row.to_dict() for row in rows],
        }
        _status_cache[cache_key] = (now, output)
        return output

    def active_world_summary(self, world: AppWorld | None) -> dict[str, Any] | None:
        if world is None:
            return None
        task = world.task
        completed = False
        try:
            completed = world.task_completed()
        except Exception:
            completed = False
        return {
            "task_id": task.id,
            "instruction": task.instruction,
            "datetime": task.datetime,
            "task_completed": completed,
            "experiment_name": world.experiment_name,
        }

    def _tasks_root(self, experiment_name: str) -> str:
        return os.path.join(path_store.experiment_outputs, experiment_name, "tasks")

    def _task_dir(self, experiment_name: str, task_id: str) -> str:
        return os.path.join(self._tasks_root(experiment_name), task_id)

    def _task_status_row(
        self,
        experiment_name: str,
        task_id: str,
        *,
        is_active: bool,
    ) -> TaskStatusRow:
        task_dir = self._task_dir(experiment_name, task_id)
        has_output = os.path.isdir(task_dir)
        finished_path = os.path.join(task_dir, "misc", "finished")
        agent_finished = os.path.isfile(finished_path)
        report_path = os.path.join(task_dir, "evaluation", "report.md")
        eval_stats = self._parse_evaluation_report(report_path)
        instruction = self._load_instruction(task_id)

        status = "not_started"
        if is_active:
            status = "active"
        if has_output:
            if eval_stats is not None:
                status = "pass" if eval_stats["success"] else "fail"
            elif agent_finished:
                status = "finished"
            elif not is_active:
                status = "in_progress"

        return TaskStatusRow(
            task_id=task_id,
            status=status,
            is_active=is_active,
            instruction=instruction,
            pass_percentage=eval_stats.get("pass_percentage") if eval_stats else None,
            pass_count=eval_stats.get("pass_count") if eval_stats else None,
            fail_count=eval_stats.get("fail_count") if eval_stats else None,
            num_tests=eval_stats.get("num_tests") if eval_stats else None,
            evaluated_at=eval_stats.get("evaluated_at") if eval_stats else None,
            has_output=has_output,
            agent_finished=agent_finished,
        )

    def _load_instruction(self, task_id: str) -> str | None:
        try:
            return Task.load(task_id=task_id).instruction
        except Exception:
            return None

    def _parse_evaluation_report(self, report_path: str) -> dict[str, Any] | None:
        if not os.path.isfile(report_path):
            return None
        with open(report_path, encoding="utf-8") as handle:
            content = handle.read()
        passed = self._parse_report_int(content, r"Num Passed Tests\s*:\s*(\d+)")
        failed = self._parse_report_int(content, r"Num Failed Tests\s*:\s*(\d+)")
        total = self._parse_report_int(content, r"Num Total\s+Tests\s*:\s*(\d+)")
        if total is None:
            return None
        pass_count = passed if passed is not None else 0
        fail_count = failed if failed is not None else 0
        mtime = os.path.getmtime(report_path)
        evaluated_at = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        success = pass_count == total and total > 0
        pass_percentage = round(100.0 * pass_count / total, 1) if total else 0.0
        return {
            "success": success,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "num_tests": total,
            "pass_percentage": pass_percentage,
            "evaluated_at": evaluated_at,
        }

    def _parse_report_int(self, content: str, pattern: str) -> int | None:
        match = re.search(pattern, content)
        if not match:
            return None
        return int(match.group(1))


def list_experiments() -> list[str]:
    return ExperimentStatus().list_experiments()


def task_status_for_experiment(
    experiment_name: str,
    *,
    task_ids: list[str] | None = None,
    dataset: str | None = None,
    active_task_id: str | None = None,
) -> dict[str, Any]:
    return ExperimentStatus().task_status_for_experiment(
        experiment_name,
        task_ids=task_ids,
        dataset=dataset,
        active_task_id=active_task_id,
    )


def active_world_summary(world: AppWorld | None) -> dict[str, Any] | None:
    return ExperimentStatus().active_world_summary(world)
