---
name: venmo-dinner-share-requests
description: After a coworkers dinner I paid the bill, shares are in Simple Note; some already paid on Venmo — make payment requests for the others with description "Work Dinner".
---

# Collect the rest of the work-dinner shares

Yesterday you treated coworkers to dinner and paid the whole bill. Individual shares are written in Simple Note. Some people already Venmo’d their share; for everyone else, send Venmo payment requests with the description note “Work Dinner”.

Sign into Simple Note and Venmo. Open the dinner-share note and list each person’s amount. Check recent Venmo activity for who already paid you toward that dinner. For each remaining coworker who still owes their share, create a payment request for the noted amount with description exactly “Work Dinner”. Do not re-request people who already settled.

## Checklist before any mutate (required)

1. **Collect first:** Simple Note — search/show the dinner note; record each person’s name, share amount, and any Venmo email/username hints.
2. **Cross-check paid:** Venmo — paginate **received** transactions (`page_limit` ≤ 20) for yesterday/today dinner-related payments. Mark who **already paid** their share.
3. **Classify:** Build the **outstanding-only** list: coworkers who still owe. Exclude anyone who already sent their share.
4. **Mutate:** `create_payment_request` **only** for outstanding shares, description exactly `Work Dinner`, correct amount per person. Do not request people who already paid (judge checks exact user_id → amount map).
5. **Verify:** Request count matches outstanding list. For action-only tasks use `complete_task` with `status: success` and **`answer: null`**. **Never** put fail prose or error explanations in `answer`.

Finish as an action-only success (no answer string).

## Tools you will need

Simple Note search/show; Venmo login, transaction history, create payment request; supervisor complete_task.
