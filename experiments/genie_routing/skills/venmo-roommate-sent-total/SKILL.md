---
name: venmo-roommate-sent-total
description: How much money have I sent to my roommates on Venmo since 1st Jan of this year — answer with the total amount.
---

# Money sent to roommates this year

This is a question. Sum how much you have sent to your roommates on Venmo since January 1 of the simulated year.

Sign into Venmo. Identify roommates, then gather outgoing transactions to them from New Year’s Day through the task clock. Add the amounts carefully. Complete the task with the **numeric (or formatted) total string** the judge expects — not null.

Do not send new payments while answering.

## Checklist before answering (required)

1. **Collect first:** Sign in. Resolve **roommate user IDs** from supervisor profile — do not assume an empty roommate list without reading profile/relationships.
2. **Paginate sent txns:** Walk **outgoing/sent** transactions from **January 1** of the simulated year through the task date. Use `page_limit` ≤ 20 and advance `page_index` until exhausted.
3. **Classify:** Sum amounts where the recipient is a roommate. Include all pages — stopping after two pages often yields `$0.00` false answers.
4. **Answer:** `complete_task` with `status: success` and the **computed total string** (e.g. dollar amount). Do not answer `$0.00` unless you verified zero sent txns to roommates after full pagination.

## Tools you will need

Venmo login and transaction history; supervisor profile for roommates; complete_task with the total as the answer.
