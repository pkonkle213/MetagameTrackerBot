---
name: Post-merge validation
description: Validation needed after merge conflict resolution in this Python bot.
---

After merging branches, run Python compilation and the complete unit-test suite before treating the merge as healthy. Git may report a clean working tree with no conflict markers even when manually combined Python blocks are syntactically or logically broken.

**Why:** The November 2026 master merge had a clean status but left Stripe payment, webhook, and test code malformed.

**How to apply:** Following every merge or conflict resolution, run `python -m compileall` on the project and `python -m pytest` across all tests, then restart the bot workflow and confirm its logs show a successful Discord connection.
