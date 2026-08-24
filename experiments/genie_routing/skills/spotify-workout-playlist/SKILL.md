---
name: spotify-workout-playlist
description: Start playing a Spotify playlist long enough for today's workout from the Simple Note workout plan, without changing playlists mid-workout.
---

# A playlist that lasts the whole workout

You need Spotify playing a playlist that will cover today’s entire workout so you never have to switch mid-session. The plan lives in Simple Note.

Sign into Simple Note and Spotify with the vault. Search notes for the workout plan (do not guess note ids). From the prompt’s simulated date, figure out the weekday on a real calendar — for example, 2023-05-25 is Thursday. In the note, find the block for that day and read its duration in minutes (`duration_mins`).

## Duration math (required)

Song lengths from `show_song` are in **seconds**. Total playlist minutes = **sum of seconds ÷ 60**.

Example: three songs of 900s, 720s, and 600s → (900 + 720 + 600) / 60 = **37.0 minutes**.

## Library scan (required)

Walk your playlist library in the order Spotify returns it. For each playlist, look up every song length and compute total minutes as above.

**Hard rule:** If total minutes **<** today’s `duration_mins`, that playlist does **not** qualify. Do **not** call `play_music` on it. Do **not** call `complete_task` with success. Keep paginating the library until you find the **first** playlist whose total minutes are **≥** `duration_mins`, then `play_music` on that playlist and stop searching.

The first qualifying playlist is often **later** in library order (e.g. playlist 183 qualifies after 182 sums to only 42.1 minutes when 45 are required). Stopping early or playing the “longest so far” below threshold fails the judge.

Do not pick the shortest among several that qualify, do not invent a temporary playlist, and do not stitch songs into a queue as a workaround.

## Token expiry

If Spotify returns an auth error mid-scan, sign in again once with the vault password, then **resume library pagination from the next page** — do not trust working-memory notes that say “no playlist found” when pagination was incomplete.

Finish as an action-only success (no answer string).

## Tools you will need

Simple Note search/show; Spotify login, playlist library/show, song show (durations), play music — not create playlist or queue helpers; supervisor complete_task.
