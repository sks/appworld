#!/usr/bin/env python3
"""Probe workout playlist durations and play_music queue for b0a8eae_3."""

from __future__ import annotations

import json

from appworld import AppWorld


def main() -> None:
    with AppWorld(
        task_id="b0a8eae_3",
        experiment_name="probe_play",
        remote_apis_url="http://127.0.0.1:9000",
    ) as world:
        passwords = world.apis.supervisor.show_account_passwords()
        spot = next(x for x in passwords if x["account_name"] == "spotify")
        sn = next(x for x in passwords if x["account_name"] == "simple_note")
        email = world.apis.supervisor.show_profile()["email"]
        tok = world.apis.spotify.login(username=email, password=spot["password"])[
            "access_token"
        ]
        world.apis.simple_note.login(username=email, password=sn["password"])
        notes = world.apis.simple_note.search_notes(query="workout", access_token=None)
        print("notes", json.dumps(notes, default=str)[:500])

        lib = world.apis.spotify.show_playlist_library(
            access_token=tok, page_index=0, page_limit=20
        )
        playlists = lib if isinstance(lib, list) else []
        if isinstance(lib, dict):
            playlists = lib.get("playlists") or lib.get("entries") or list(lib.values())
        print("library_n", len(playlists) if isinstance(playlists, list) else type(playlists))

        results = []
        for pl in playlists[:20]:
            if not isinstance(pl, dict):
                continue
            pid = pl.get("playlist_id") or pl.get("id")
            detail = world.apis.spotify.show_playlist(
                playlist_id=pid, access_token=tok
            )
            songs = detail.get("songs") or []
            ids = [s.get("id") or s.get("song_id") for s in songs]
            total = 0
            for sid in ids:
                song = world.apis.spotify.show_song(song_id=sid)
                total += int(song["duration"])
            results.append(
                (pid, detail.get("title"), len(ids), total, round(total / 60.0, 3), ids)
            )

        results.sort(key=lambda x: x[3])
        for r in results:
            print(
                f"pl={r[0]} title={r[1]!r} n={r[2]} sec={r[3]} min={r[4]}"
            )

        for pid in (184, 179):
            print(f"--- play {pid} ---")
            print(
                world.apis.spotify.play_music(access_token=tok, playlist_id=pid)
            )
            player = world.apis.spotify.show_current_song(access_token=tok)
            print("current", player)
            # try music player endpoints
            for name in (
                "show_music_player",
                "show_song_queue",
                "show_queue",
            ):
                fn = getattr(world.apis.spotify, name, None)
                if fn is None:
                    continue
                try:
                    out = fn(access_token=tok)
                    print(name, json.dumps(out, default=str)[:600])
                except Exception as exc:  # noqa: BLE001
                    print(name, "ERR", exc)


if __name__ == "__main__":
    main()
