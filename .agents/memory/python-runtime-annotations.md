---
name: Runtime type annotations
description: Import requirements for runtime-evaluated Python annotations in this project.
---

Python evaluates annotations at module import unless postponed annotation evaluation is enabled, so a type used only in an annotation can still be a required runtime import.

**Why:** Removing apparently unused domain-type imports caused module imports to fail with `NameError`.

**How to apply:** When cleaning imports from service modules, keep every referenced annotation type imported or explicitly enable postponed evaluation, then run an import or compile check.
