---
name: Async modal loading
description: Load database-backed Discord modal choices before opening the modal without making its constructor async.
---

Keep Discord modal constructors synchronous. When a modal needs database-backed choices, fetch them in an awaited async class factory or loader, then pass the data into the constructor before sending the modal.

**Why:** Python constructors cannot be awaited, and Discord requires a fully built modal when the interaction is used to open it.

**How to apply:** For new modals with async data dependencies, provide an async factory and make every command or service call site await it before `interaction.response.send_modal(...)`.