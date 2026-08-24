#!/usr/bin/env python3
"""Init is assumed done; play playlist 183 and print queue + local evaluate."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request


def req(method: str, url: str, data=None, headers=None, form=False):
    h = dict(headers or {})
    body = None
    if data is not None and form:
        body = urllib.parse.urlencode(data).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)


def main() -> None:
    base = "http://127.0.0.1:9000"
    profile = req("GET", f"{base}/supervisor/profile")
    email = profile["email"]
    print("email", email)
    pw = req("GET", f"{base}/supervisor/account_passwords")
    spot = next(x for x in pw if x["account_name"] == "spotify")
    login = req(
        "POST",
        f"{base}/spotify/auth/token",
        {"username": email, "password": spot["password"], "grant_type": "password"},
        form=True,
    )
    tok = login["access_token"]
    print("login ok")
    play = req(
        "POST",
        f"{base}/spotify/music_player/play",
        {"playlist_id": 183},
        headers={"Authorization": f"Bearer {tok}"},
    )
    print("play", play)
    queue = req(
        "GET",
        f"{base}/spotify/music_player/song_queue",
        headers={"Authorization": f"Bearer {tok}"},
    )
    print("queue_n", len(queue), [s.get("song_id") for s in queue])
    # complete_task
    done = req(
        "POST",
        f"{base}/supervisor/complete_task",
        {"status": "success", "answer": None},
    )
    print("complete", done)


if __name__ == "__main__":
    main()
