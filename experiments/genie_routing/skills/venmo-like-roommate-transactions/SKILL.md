---
name: venmo-like-roommate-transactions
description: Like all the Venmo transactions from today involving any of my roommates on my Venmo social feed.
---

# Like today’s roommate Venmo activity

On today’s simulated date, your Venmo social feed may show transactions that involve your roommates. Like each of those.

Sign into Venmo. Learn who your roommates are from the supervisor profile or related relationship data the apps expose. Open today’s social feed (paginate if needed) and like every transaction that involves any roommate — payments you appear in with them, or activity clearly tied to them. Skip older days and people who are not roommates.

## Checklist before any mutate (required)

1. **Collect first:** Sign in. Resolve **roommate user IDs** from supervisor profile / relationships before opening the feed.
2. **Paginate feed:** Call `show_social_feed` with `page_limit` **≤ 20** and increment `page_index` until a page returns no new today’s transactions. **Do not** stop after page 0 only.
3. **Classify:** From all pages, list every **today** transaction ID that involves any roommate (payer, payee, or tagged participant).
4. **Mutate all:** `like_transaction` on **each** ID in that set. The judge checks the full set — liking one of four fails the errand.
5. **Verify:** Number of likes must equal the classified set size before `complete_task` success.

Finish as an action-only success (no answer string).

## Tools you will need

Venmo login, social feed, like transaction; supervisor profile/passwords, complete_task.
