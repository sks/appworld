---
name: spotify-rate-liked-songs
description: Give a 5-star rating to all songs in my Spotify playlists which I have liked; if already rated lower, increase it to 5.
---

# Five stars for every liked playlist song

You want every song you have liked that appears in your Spotify playlists to carry a five-star rating. If a song is already rated below five, raise it; if it is already five, leave it alone.

Sign into Spotify. Walk the playlist library and, for each track, check whether you have liked it. For liked songs whose rating is missing or below five, set the rating to five. Do not touch songs you have not liked, and do not invent a separate “rate everything” sweep beyond the playlists.

## Checklist before any mutate (required)

1. **Collect first:** Paginate **all** playlists (`page_limit` ≤ 20 per call). For each playlist, paginate songs. Build a master list of `(song_id, liked?, current_rating?)` for tracks in playlists only.
2. **Classify:** Subset where `liked == true` AND (`rating < 5` OR rating missing). This is your mutate list — do not rate unliked songs.
3. **Mutate with correct API:** For each song on the list:
   - No existing review → `review_song` with rating 5 (`appworld_spotify__review_song`)
   - Existing review below 5 → `update_song_review` to 5
   AppWorld has **`review_song`** (add) and **`update_song_review`** (update) — there is no `add_song_review`. Using only `update_song_review` when add is required fails the judge's song_id sets.
4. **Verify:** Every liked playlist song that needed a bump must appear in changed reviews. Missing one song fails TGC.

Finish as an action-only success (no answer string).

## Tools you will need

Spotify login, playlist library/song inspection, `review_song`, `update_song_review`; supervisor complete_task.
