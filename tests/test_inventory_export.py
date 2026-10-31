import csv
import io
import unittest
from unittest.mock import AsyncMock, Mock, patch

from commands.inventory_commands import InventoryCommands
from services.inventory_service import BuildMoxfieldHavesCsv, ExportInventoryCsv


MOXFIELD_HEADERS = [
    "Count",
    "Tradelist Count",
    "Name",
    "Edition",
    "Condition",
    "Language",
    "Foil",
    "Tags",
    "Last Modified",
    "Collector Number",
    "Alter",
    "Proxy",
    "Purchase Price",
]


class InventoryCsvExportTests(unittest.IsolatedAsyncioTestCase):
    def test_exports_reference_headers_and_inventory_values(self):
        content = BuildMoxfieldHavesCsv([(3, "Sol Ring", "CMR")]).decode("utf-8")
        rows = list(csv.reader(io.StringIO(content)))

        self.assertEqual(rows[0], MOXFIELD_HEADERS)
        self.assertEqual(
            rows[1][:8],
            ["3", "3", "Sol Ring", "cmr", "Near Mint", "English", "", ""],
        )
        self.assertTrue(rows[1][8])
        self.assertEqual(rows[1][9:], ["", "False", "False", ""])

    def test_empty_inventory_still_exports_moxfield_headers(self):
        rows = list(csv.reader(io.StringIO(BuildMoxfieldHavesCsv([]).decode("utf-8"))))
        self.assertEqual(rows, [MOXFIELD_HEADERS])

    async def test_export_service_reads_all_inventory(self):
        with patch(
            "services.inventory_service.GetAllInventory",
            new=AsyncMock(return_value=[(2, "Island", "DMU")]),
        ) as get_inventory:
            content = await ExportInventoryCsv()

        get_inventory.assert_awaited_once_with()
        row = list(csv.reader(io.StringIO(content.decode("utf-8"))))[1]
        self.assertEqual(row[0:4], ["2", "2", "Island", "dmu"])

    async def test_export_command_sends_csv_file_ephemerally(self):
        cog = InventoryCommands(Mock())
        interaction = Mock()
        interaction.response.defer = AsyncMock()
        interaction.followup.send = AsyncMock()

        with patch(
            "commands.inventory_commands.ExportInventoryCsv",
            new=AsyncMock(return_value=b"Count,Name\n"),
        ):
            await InventoryCommands.Export.callback(cog, interaction)

        interaction.response.defer.assert_awaited_once_with(
            ephemeral=True, thinking=True
        )
        sent_file = interaction.followup.send.await_args.kwargs["file"]
        self.assertEqual(sent_file.filename, "moxfield_haves.csv")
        self.assertTrue(interaction.followup.send.await_args.kwargs["ephemeral"])


if __name__ == "__main__":
    unittest.main()
