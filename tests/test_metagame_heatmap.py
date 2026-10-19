import unittest
from decimal import Decimal
from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch

from PIL import Image

from data.metagame_heatmap_data import MetagameHeatmapRow
from services import metagame_heatmap_services as heatmap_services
from services.metagame_heatmap_services import (
    BuildMetagameHeatmapImage,
    CELL_HEIGHT,
    CELL_WIDTH,
    GRID_LEFT,
    GRID_TOP,
    LEFT_MARGIN,
    MAX_HEATMAP_DECKS,
    OVERALL_WIDTH,
    SelectTopArchetypes,
)


class MetagameHeatmapImageTests(unittest.TestCase):
    def make_rows(self, count: int) -> list[MetagameHeatmapRow]:
        rows = []
        for index in range(count):
            opponent_index = (index + 1) % count
            rows.append(
                MetagameHeatmapRow(
                    f"Deck {index + 1}",
                    count - index,
                    55.0 - index,
                    f"Deck {opponent_index + 1}",
                    12,
                    48.5 + index,
                )
            )
        return rows

    def test_selects_the_16_most_played_archetypes(self):
        rows = self.make_rows(20)

        archetypes, _, _ = SelectTopArchetypes(rows)

        self.assertEqual(len(archetypes), MAX_HEATMAP_DECKS)
        self.assertEqual(archetypes[0], "Deck 1")
        self.assertEqual(archetypes[-1], "Deck 16")

    def test_builds_a_png_with_space_for_matrix_and_overall_rates(self):
        image_bytes = BuildMetagameHeatmapImage(
            "Standard heatmap", self.make_rows(20)
        )

        image = Image.open(BytesIO(image_bytes))
        self.assertEqual(image.format, "PNG")
        self.assertEqual(
            image.size,
            (
                GRID_LEFT + MAX_HEATMAP_DECKS * CELL_WIDTH + 36,
                GRID_TOP + MAX_HEATMAP_DECKS * CELL_HEIGHT + 44,
            ),
        )

    def test_overall_column_is_between_deck_labels_and_matchup_grid(self):
        self.assertGreater(GRID_LEFT, LEFT_MARGIN + OVERALL_WIDTH)

    def test_renders_small_metagames_without_empty_result(self):
        image_bytes = BuildMetagameHeatmapImage(
            "Small heatmap", self.make_rows(2)
        )

        image = Image.open(BytesIO(image_bytes))
        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)

    def test_win_rate_cells_use_translucent_red_and_green_tints(self):
        red = heatmap_services._WinRateColor(30)
        neutral = heatmap_services._WinRateColor(50)
        green = heatmap_services._WinRateColor(70)

        self.assertGreater(int(red[1:3], 16), int(red[3:5], 16))
        self.assertEqual(neutral, "#FFFFFF")
        self.assertGreater(int(green[3:5], 16), int(green[1:3], 16))
        self.assertNotEqual(red, "#DC3545")
        self.assertNotEqual(green, "#28A745")
        self.assertEqual(heatmap_services._WinRateColor(Decimal("30.0")), red)


class MetagameHeatmapDeliveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_sends_the_chart_attachment_ephemerally(self):
        interaction = Mock()
        interaction.followup.send = AsyncMock()

        with patch.object(
            heatmap_services, "BuildMetagameHeatmapImage", return_value=b"png"
        ):
            await heatmap_services.SendMetagameHeatmap(
                interaction, "Heatmap", []
            )

        interaction.followup.send.assert_awaited_once()
        call = interaction.followup.send.await_args
        self.assertTrue(call.kwargs["ephemeral"])
        self.assertEqual(call.kwargs["file"].filename, "metagame_heatmap.png")


if __name__ == "__main__":
    unittest.main()
