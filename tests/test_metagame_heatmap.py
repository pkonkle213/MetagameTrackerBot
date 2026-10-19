import unittest
from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch

from PIL import Image

from data.metagame_heatmap_data import MetagameHeatmapRow
from services import metagame_heatmap_services as heatmap_services
from services.metagame_heatmap_services import (
    BuildMetagameHeatmapImage,
    CELL_HEIGHT,
    CELL_WIDTH,
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
                LEFT_MARGIN
                + MAX_HEATMAP_DECKS * CELL_WIDTH
                + 20
                + OVERALL_WIDTH
                + 36,
                GRID_TOP + MAX_HEATMAP_DECKS * CELL_HEIGHT + 44,
            ),
        )

    def test_renders_small_metagames_without_empty_result(self):
        image_bytes = BuildMetagameHeatmapImage(
            "Small heatmap", self.make_rows(2)
        )

        image = Image.open(BytesIO(image_bytes))
        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)


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
