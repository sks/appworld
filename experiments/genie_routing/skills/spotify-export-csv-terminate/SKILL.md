---
name: spotify-export-csv-terminate
description: Export a unique list of all songs from my Spotify song library, album library, and playlists into ~/backups/spotify.csv with Title and Artists headers (artists separated by |), then terminate my Spotify account.
---

# Backup Spotify songs, then close the account

You need a unique song list written to a CSV under backups in the File System, then you terminate the Spotify account.

Sign into Spotify and the File System. Collect songs from the song library, album library, and every playlist. Deduplicate so each song appears once. Build a CSV with headers `Title` and `Artists`, using `|` between artists on a row. Ensure the backups directory exists, write `~/backups/spotify.csv`, and only after that backup is in place terminate the Spotify account as the product allows.

## Auth gate (hard)

1. Read supervisor vault password for Spotify before login.
2. If login returns **Invalid credentials**, re-read vault once and retry login **once**.
3. If login still fails after retry, call `complete_task` with **`status: fail`** — do not mark success with an empty CSV or skip terminate silently.

## Checklist before terminate (required)

1. **Collect:** After successful login, paginate song library, album library, and every playlist (`page_limit` ≤ 20). Deduplicate by song identity; build title → artists map.
2. **Write CSV:** File System — ensure `~/backups/` exists; write `~/backups/spotify.csv` with headers `Title`,`Artists` and `|` between artist names.
3. **Verify file:** Confirm the CSV is non-empty and keys match expected song titles before any account termination.
4. **Terminate:** Only after a verified backup, call **`delete_account`** on Spotify (`appworld_spotify__delete_account` — there is no `terminate_account` tool).

Finish as an action-only success (no answer string). Do not terminate before the file is written correctly.

## Tools you will need

Spotify login, library/playlist reads, **`delete_account`**; File System **`create_directory`** + **`create_file`** (not `write_file`); supervisor complete_task.
