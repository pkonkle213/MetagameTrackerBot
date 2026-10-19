---
name: Metagame heatmap output
description: Product expectations for the Discord metagame heatmap command.
---

The `/metagame_heatmap` command should privately send a chart image for the 16 most-played archetypes in the mapped format. Include each deck's overall win percentage and each head-to-head win percentage with games played. Label matchup columns with archetype names, not numeric keys, and use translucent red for lower win rates and translucent green for higher rates. Preserve the existing `/metagame` command.

**Why:** The user explicitly requested this output and visual treatment, and chose the non-breaking `/metagame_heatmap` route.

**How to apply:** Keep chart ranking, labels, colors, metrics, image output, and ephemeral visibility consistent when changing this command.
