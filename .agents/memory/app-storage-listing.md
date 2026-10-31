---
name: App Storage listing metadata
description: How the installed Replit App Storage SDK exposes object upload times.
---

The public `Client.list()` result contains object names only, not update timestamps. Sorting those names does not establish which file was uploaded most recently. When recency matters, obtain each object's storage `updated` metadata through a narrowly scoped adapter and fail explicitly if timestamps are unavailable.

**Why:** Inventory sync must pick the actual latest upload rather than a lexicographically greatest filename.

**How to apply:** Keep metadata-specific access isolated in `services/object_storage_service.py`; verify compatibility if the Replit SDK changes.
