---
name: spotify-most-liked-song
description: What is the title of the most-liked song in my Spotify playlists — answer with the song title.
---

# The most-liked song across playlists

This is a question, not a side-effect errand. You need the title of the song that has the most likes among songs appearing in your Spotify playlists.

Sign into Spotify with the vault. Paginate through the playlist library. For each playlist, inspect its tracks and note each song’s like count (or equivalent likes field). Track the song with the highest like count you have seen. When the library is fully scanned, finish by completing the task with the **exact title string** returned by the API — not blank, not null, and not a paraphrase.

Do not create playlists or change ratings while answering.

## Tools you will need

Spotify login, playlist library/show, song details; supervisor complete_task with the title as the answer.
