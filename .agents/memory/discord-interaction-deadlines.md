---
name: Discord interaction deadlines
description: How to order database work around Discord modal and component responses.
---

Send a modal or otherwise acknowledge a Discord interaction before performing synchronous database or network work.

**Why:** Production database latency caused a confirmation-button interaction to expire before `send_modal()`, producing Discord error 10062 even though the same flow was fast enough in development.

**How to apply:** For component-to-modal flows, open the modal immediately because a deferred interaction cannot later open one. Move persistence after modal submission or final confirmation, whose callbacks can defer first.