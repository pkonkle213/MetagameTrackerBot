import unittest

from data.metagame_heatmap_data import MetagameHeatmapRow
from services.metagame_heatmap_services import BuildMetagameHeatmapMessages


class MetagameHeatmapOutputTests(unittest.TestCase):
    def test_ranks_archetypes_and_shows_overall_and_matchup_rates(self):
        rows = [
            MetagameHeatmapRow("Deck A", 10, 55.0, "Deck B", 3, 66.7),
            MetagameHeatmapRow("Deck B", 5, 40.0, "Deck A", 3, 33.3),
            MetagameHeatmapRow("Deck C", 1, None, None, None, None),
        ]

        messages = BuildMetagameHeatmapMessages("Heatmap title", rows)
        output = "\n".join(messages)

        self.assertLess(output.index("1. Deck A"), output.index("2. Deck B"))
        self.assertLess(output.index("2. Deck B"), output.index("3. Deck C"))
        self.assertIn("overall win rate: 55.0%", output)
        self.assertIn("vs Deck B: 66.7% (3 games)", output)
        self.assertIn("vs Deck A: 33.3% (3 games)", output)
        self.assertIn("vs Deck C: N/A (0 games)", output)
        self.assertIn("overall win rate: N/A", output)

    def test_splits_long_heatmaps_under_discord_message_limit(self):
        rows = []
        for index in range(18):
            for opponent_index in range(18):
                if index != opponent_index:
                    rows.append(
                        MetagameHeatmapRow(
                            f"Deck {index}",
                            18 - index,
                            50.0,
                            f"Deck {opponent_index}",
                            4,
                            50.0,
                        )
                    )

        messages = BuildMetagameHeatmapMessages("Heatmap title", rows)

        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(message) <= 1900 for message in messages))


if __name__ == "__main__":
    unittest.main()
