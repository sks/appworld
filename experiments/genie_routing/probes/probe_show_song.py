#!/usr/bin/env python3
"""Probe Spotify show_song / show_playlist for b0a8eae_3 inside the stack container."""

from __future__ import annotations

import json

from appworld import AppWorld


def main() -> None:
    with AppWorld(
        task_id="b0a8eae_3",
        experiment_name="probe_show_song",
        remote_apis_url="http://127.0.0.1:9000",
    ) as world:
        passwords = world.apis.supervisor.show_account_passwords()
        spot = next(x for x in passwords if x.get("account_name") == "spotify")
        email = world.apis.supervisor.show_profile()["email"]
        print("email", email)
        tok = world.apis.spotify.login(username=email, password=spot["password"])
        access = tok["access_token"] if isinstance(tok, dict) else tok
        print("login ok")

        for song_id in (1, 54, 100):
            try:
                song = world.apis.spotify.show_song(song_id=song_id)
                print(f"show_song({song_id}) OK keys={list(song)[:8] if isinstance(song, dict) else type(song)}")
                if isinstance(song, dict):
                    print("  duration", song.get("duration"), "title", song.get("title"))
            except Exception as exc:  # noqa: BLE001
                print(f"show_song({song_id}) ERR {type(exc).__name__}: {exc}")

        for playlist_id in (183, 321, 59):
            try:
                pl = world.apis.spotify.show_playlist(
                    playlist_id=playlist_id, access_token=access
                )
                songs = pl.get("songs") if isinstance(pl, dict) else None
                n = len(songs) if songs else 0
                print(f"show_playlist({playlist_id}) OK song_count={n}")
                if songs:
                    s0 = songs[0]
                    print(
                        "  first",
                        {
                            k: s0.get(k)
                            for k in ("id", "song_id", "duration", "title")
                            if isinstance(s0, dict)
                        },
                    )
            except Exception as exc:  # noqa: BLE001
                print(f"show_playlist({playlist_id}) ERR {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
