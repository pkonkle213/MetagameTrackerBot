import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from commands.inventory_commands import InventoryCommands
from data.inventory_data import AddReceivedInventory
from custom_errors import KnownError
from input_modals.inventory_received_modal import InventoryReceivedModal
from services.inventory_service import ParseReceivedInventoryInput, ReceiveInventory


class ReceivedInventoryParsingTests(unittest.TestCase):
    def test_parses_card_quantities_names_and_editions(self):
        self.assertEqual(
            ParseReceivedInventoryInput(
                "2 Sol Ring - CMR\n\n4 Island - DMU"
            ),
            [(2, "Sol Ring", "CMR"), (4, "Island", "DMU")],
        )

    def test_rejects_invalid_or_empty_input(self):
        for text in ("", "Card - SET", "0 Card - SET", "2 Card without edition"):
            with self.subTest(text=text), self.assertRaises(KnownError):
                ParseReceivedInventoryInput(text)


class ReceivedInventoryDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_increments_exact_match_and_inserts_unmatched_edition(self):
        connection = AsyncMock()
        connection.__aenter__.return_value = connection
        cursor = AsyncMock()
        cursor.__aenter__.return_value = cursor
        cursor.fetchone = AsyncMock(side_effect=[(17,), None])
        connection.cursor = Mock(return_value=cursor)

        with patch(
            "data.inventory_data.AsyncConnection.connect",
            new=AsyncMock(return_value=connection),
        ):
            result = await AddReceivedInventory(
                [(2, "Sol Ring", "CMR"), (4, "Island", "DMU")]
            )

        self.assertEqual(result, (1, 1))
        calls = cursor.execute.await_args_list
        self.assertIn("LOCK TABLE inventory", calls[3].args[0])
        self.assertEqual(calls[4].args[1], ["Sol Ring", "CMR"])
        self.assertIn("UPDATE inventory", calls[5].args[0])
        self.assertEqual(calls[5].args[1], [2, 17])
        self.assertEqual(calls[6].args[1], ["Island", "DMU"])
        self.assertIn("INSERT INTO inventory", calls[7].args[0])
        self.assertEqual(calls[7].args[1], [4, "Island", "DMU"])
        connection.commit.assert_awaited_once()

    async def test_service_parses_before_writing(self):
        with patch(
            "services.inventory_service.AddReceivedInventory",
            new=AsyncMock(return_value=(1, 0)),
        ) as add:
            result = await ReceiveInventory("3 Forest - MKM")

        self.assertEqual(result, (1, 0))
        add.assert_awaited_once_with([(3, "Forest", "MKM")])


class ReceivedInventoryCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_received_command_opens_modal(self):
        cog = InventoryCommands(Mock())
        interaction = Mock()
        interaction.response.send_modal = AsyncMock()
        modal = object()

        with patch(
            "commands.inventory_commands.InventoryReceivedModal",
            return_value=modal,
        ):
            await InventoryCommands.Received.callback(cog, interaction)

        interaction.response.send_modal.assert_awaited_once_with(modal)

    async def test_modal_processes_received_lines_and_reports_counts(self):
        modal = InventoryReceivedModal(Mock())
        modal.cards = SimpleNamespace(
            component=SimpleNamespace(value="2 Sol Ring - CMR")
        )
        interaction = Mock()
        interaction.response.defer = AsyncMock()
        interaction.followup.send = AsyncMock()

        with patch(
            "input_modals.inventory_received_modal.ReceiveInventory",
            new=AsyncMock(return_value=(1, 0)),
        ) as receive:
            await modal.on_submit(interaction)

        receive.assert_awaited_once_with("2 Sol Ring - CMR")
        interaction.followup.send.assert_awaited_once_with(
            "Inventory received: 1 existing entries updated; 0 new entries added.",
            ephemeral=True,
        )


if __name__ == "__main__":
    unittest.main()
