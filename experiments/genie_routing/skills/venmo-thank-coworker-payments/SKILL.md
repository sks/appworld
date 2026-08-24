---
name: venmo-thank-coworker-payments
description: Add a comment "Thank you!" to all Venmo payments I received from my coworkers in the last 5 days including today, and like those payments.
---

# Thank coworkers for recent Venmo payments

Over the last five days of simulated time (including today), coworkers have sent you Venmo payments. Comment “Thank you!” on each of those payments and like them.

Sign into Venmo. Identify coworkers from relationships the apps expose. Scan received payments (or the feed) across that five-day window. For each payment from a coworker in range, add the exact thank-you comment and like the payment. Skip payments outside the window and skip non-coworkers.

## Checklist before any mutate (required)

1. **Collect first:** Sign in to Venmo. Read `show_profile` and supervisor relationships. Resolve **coworker user IDs** via phone `search_contacts` or profile relationship fields — do not assume “no coworkers” without checking both Venmo and phone.
2. **Date window:** Derive the five-day window from the task’s simulated “today” (including today). Record each **received** payment’s `transaction_id`, sender, and date. Drop anything outside the window.
3. **Classify:** Keep only payments whose sender is a coworker. Build the full list of transaction IDs to mutate **before** liking or commenting.
4. **Mutate all:** For **every** ID on the list: `like_transaction` then `create_transaction_comment` with text exactly `Thank you!`. Missing even one fails the judge.
5. **Verify:** Like count + comment count must equal the coworker payment count. **Never** call `complete_task` with `status: success` if you performed **zero** likes and comments — that is a false success.

Finish as an action-only success (no answer string).

## Tools you will need

Venmo login, `show_transactions` / payment history, `like_transaction`, `create_transaction_comment`; supervisor profile/passwords, phone `search_contacts`; complete_task.
