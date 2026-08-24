#!/usr/bin/env python3
"""Patch installed AppWorld Spotify Song humanize to include album_title.

PyPI apps.bundle omits album_title in Song._to_humanized_dict. FastAPI then
rejects Song:default / shortened / queue responses with HTTP 500, which blocks
agents from reading durations (show_song) and verifying queues (show_song_queue).
"""

from __future__ import annotations

from pathlib import Path


def _patch_models() -> bool:
    path = Path("/usr/local/lib/python3.12/site-packages/appworld/apps/spotify/models.py")
    text = path.read_text()
    if 'song_dict["album_title"]' in text:
        print("models already patched")
        return False
    old = (
        '        song_dict["artists"] = [{"id": artist.id, "name": artist.name} for artist in artists]\n'
        '        if name == "shortened":\n'
    )
    new = (
        '        song_dict["artists"] = [{"id": artist.id, "name": artist.name} for artist in artists]\n'
        "        album = self.album\n"
        '        song_dict["album_title"] = album.title if album is not None else ""\n'
        '        if name == "shortened":\n'
    )
    if old not in text:
        raise SystemExit("Song._to_humanized_dict artists block not found")
    path.write_text(text.replace(old, new, 1))
    print(f"patched {path}")
    return True


def _patch_apis_show_song() -> bool:
    """Defense in depth if models patch is skipped on an older layout."""
    path = Path("/usr/local/lib/python3.12/site-packages/appworld/apps/spotify/apis.py")
    text = path.read_text()
    changed = False
    if "_enrich_song_dict" not in text:
        needle = "from appworld.common.utils import unique_list_of\n\n\nlogin_by"
        insert = (
            "from appworld.common.utils import unique_list_of\n\n\n"
            "def _enrich_song_dict(song: dict) -> dict:\n"
            '    """Ensure album_title is present for FastAPI response validation."""\n'
            '    if song.get("album_title") is not None:\n'
            "        return song\n"
            '    album_id = song.get("album_id")\n'
            "    if album_id is None:\n"
            '        song["album_title"] = ""\n'
            "        return song\n"
            "    album = models.Album.by_id(album_id)\n"
            '    song["album_title"] = album.title if album is not None else ""\n'
            "    return song\n\n\n"
            "login_by"
        )
        if needle not in text:
            print("apis enrich needle not found — skip apis helper")
        else:
            text = text.replace(needle, insert, 1)
            changed = True
    old = (
        "    song = models.Song.by_id_or_raise(song_id)\n"
        "    return song.to_dict(humanize=True)"
    )
    new = (
        "    song = models.Song.by_id_or_raise(song_id)\n"
        "    return _enrich_song_dict(song.to_dict(humanize=True))"
    )
    if old in text and "_enrich_song_dict(song.to_dict(humanize=True))" not in text:
        text = text.replace(old, new, 1)
        changed = True
    if changed:
        path.write_text(text)
        print(f"patched {path}")
        return True
    print("apis show_song already patched or unchanged")
    return False


def main() -> None:
    _patch_models()
    _patch_apis_show_song()


if __name__ == "__main__":
    main()
