---
name: Dependency security floors
description: Why security-related transitive dependencies have explicit minimum versions.
---

Keep explicit minimum safe versions for remediated transitive dependencies even when application code does not import them directly.

**Why:** Updating only the lockfile resolves the immediate findings but permits a future dependency resolution to select vulnerable versions allowed by upstream packages. These minimums intentionally supplement upstream requirements.

**How to apply:** During dependency cleanup, do not remove a security floor solely because it appears unused. Confirm that upstream requirements enforce an equally safe minimum before removing it.
