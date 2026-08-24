---
name: spotify-cleanup-liked-downloaded
description: Cleanup Spotify libraries — keep only songs and albums I have liked or downloaded; an album counts as downloaded if all its songs are downloaded; leave playlists unchanged.
---

# Keep only liked or downloaded songs and albums

Clean the song and album libraries so only liked or downloaded items remain. An album is downloaded only when every song on it is downloaded. Leave the playlist library untouched.

Sign into Spotify. Inspect each song in the song library: keep it if liked or downloaded; otherwise remove it. For each album, keep it if liked or fully downloaded; otherwise remove it. Do not edit playlists as part of this cleanup.

Finish as an action-only success (no answer string).

## Tools you will need

Spotify login, song/album library reads, like/download flags, remove mutates; supervisor complete_task.
