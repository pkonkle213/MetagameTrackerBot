---
name: Discord interaction acknowledgements
description: Rules for button and modal flows that must respond within Discord's interaction window.
---

Every Discord component callback must acknowledge its interaction immediately. If the next step is a modal, open that modal from the callback itself; deferring first consumes the response and prevents a later modal response. Longer work should use follow-up messages after the initial acknowledgement.

**Why:** Waiting for a view and responding later can expire the component interaction, producing “didn't respond in time” errors.

**How to apply:** When a button starts a modal or database operation, make the callback perform the immediate response and move slow work after that response.