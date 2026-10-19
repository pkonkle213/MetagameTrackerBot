---
name: Metagame heatmap output
description: Product expectations for the Discord metagame heatmap command.
---

The `/metagame_heatmap` command should privately send a chart image for the 16 most-played archetypes in the mapped format. Include each deck's overall win percentage and each head-to-head win percentage with games played. Place overall win percentage between each archetype row label and the matchup grid; size its column position from the widest selected row label with a small gap. Keep the “Opponent archetype” heading near the red/green guide; size the column-label area and grid top according to the longest selected archetype. Bottom-align matchup column names just above the head-to-head cells. Use archetype names, not numeric keys, with translucent red for lower win rates and translucent green for higher rates. Preserve the existing `/metagame` command.

Normalize database `Decimal` win-rate values before doing color arithmetic; psycopg numeric values are not interchangeable with floats in mixed arithmetic.

**Why:** The user explicitly requested this output and visual treatment, and a live invocation exposed Decimal/float arithmetic incompatibility.

**How to apply:** Keep chart ranking, column order, label placement, colors, metrics, image output, and ephemeral visibility consistent when changing this command; normalize numeric types at rendering boundaries.
