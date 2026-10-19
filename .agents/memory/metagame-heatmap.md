---
name: Metagame heatmap output
description: Product expectations for the Discord metagame heatmap command.
---

The `/metagame_heatmap` command should privately send a chart image for the 16 most-played archetypes in the mapped format. Include each deck's overall win percentage and each head-to-head win percentage with games played. Preserve the existing `/metagame` command.

**Why:** The user explicitly requested this output and chose the non-breaking `/metagame_heatmap` route.

**How to apply:** Keep chart ranking, metrics, image output, and ephemeral visibility consistent when changing this command.
