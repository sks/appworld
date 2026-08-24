---
name: splitwise-invite-sms
description: Splitwise group invitations arrived over phone text this week; accept invites whose sender is in my phone contacts, otherwise delete those messages.
---

# Splitwise invites in this week’s texts

You have received Splitwise group invitations by SMS during the simulated “this week.” Treat that week as relative to the task’s fixed calendar clock, not today’s real-world date. Message timestamps in 2023 are still current for this world — do not discard them for looking old.

Sign into Phone and Splitwise via the password vault. Search Phone texts for Splitwise invites and **paginate until there are no more pages**.

## Week window (hard filter)

Only process invite SMS whose **`sent_at` falls in the simulated “this week”** window derived from the prompt’s fixed datetime (e.g. 2023-05-18 → invites sent 2023-05-15 through 2023-05-21). **Ignore** invites outside that window even when the sender is in contacts — accepting an old invite (e.g. code `888d2` sent 2023-05-06) fails the judge and must not be accepted or deleted.

## Checklist before any mutate (required)

1. **Collect first:** Walk every page of Splitwise invite texts. For each message, record `message_id`, `sent_at`, invitation code, and whether sender has `contact_id`. **Drop any invite whose `sent_at` is outside the simulated week** before building the mutate list.
2. **Classify each code:** For each message, decide contact vs non-contact (via `contact_id` on the message or `search_contacts` on the sender number).
3. **Accept all contact codes:** Call `accept_group_invitation` on Splitwise for **every** contact-sender code on your list. Missing even one required accept fails the errand — the judge checks the full set of group_ids.
4. **Delete non-contacts:** Only after all contact accepts succeed, delete **every** non-contact invite SMS in the week window. Paginate phone search until exhausted — missing even one required delete fails the judge.

Duplicates and retries must not cause you to skip a code still outstanding. If an accept fails with auth error, sign into Splitwise again once with the vault password and retry **that same invitation code** before moving on. Do not drop remaining codes on retry.

Process contact accepts first, then delete non-contact invite messages. Every in-week non-contact invite must be deleted; missing one fails the errand. Do not delete messages you accepted, do not delete invites whose senders are contacts, and do not touch older invites outside the week window. A second invite from the same contact still needs its own accept with that message’s code.

Finish as an action-only success (no answer string).

## Tools you will need

Phone login, search/show/delete texts, search contacts; Splitwise login and accept group invitation; supervisor profile, passwords, complete_task.
