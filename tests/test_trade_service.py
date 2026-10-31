import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from custom_errors import KnownError
from commands.trade_quote_command import TradeQuoteCommand
from input_modals.inventory_trade_modal import InventoryTradeModal
from services.trade_service import BuildTradeTable, ParseTradeInput, BuildTrade


class TradeParsingTests(unittest.TestCase):
    def test_parses_supported_quantity_formats_and_combines_blanks(self):
        self.assertEqual(
            ParseTradeInput("2 Card One\n3x Card Two\n1 - Card Three\n"),
            [(2, "Card One"), (3, "Card Two"), (1, "Card Three")],
        )

    def test_rejects_invalid_trade_lines(self):
        with self.assertRaises(KnownError):
            ParseTradeInput("Card without a quantity")

    def test_table_rounds_unit_price_to_quarter_and_total_to_five(self):
        messages, grand_total = BuildTradeTable(
            [("Card", 3, 246, 250, 750)]
        )
        self.assertEqual(grand_total, 1000)
        output = "\n".join(messages)
        self.assertIn("$2.46", output)
        self.assertIn("$2.50", output)
        self.assertIn("$10.00", output)


class TradeExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_caps_trade_to_stock_and_deducts_only_after_quote_is_built(self):
        card = {
            "name": "Sol Ring",
            "set": "cmr",
            "set_name": "Commander Legends",
            "collector_number": "335",
            "id": "scryfall-card-id",
        }
        with (
            patch(
                "services.trade_service.GetInventoryForNames",
                new=AsyncMock(return_value=[(17, "Sol Ring", "cmr", 2)]),
            ),
            patch(
                "services.trade_service._EnsureCachedFile",
                side_effect=lambda _name, _ttl, path, _url: path,
            ),
            patch(
                "services.trade_service._LoadScryfallPrintings",
                return_value={("sol ring", "cmr"): [card]},
            ),
            patch(
                "services.trade_service._LoadNormalPrices",
                return_value={"scryfall-card-id": 246},
            ),
            patch(
                "services.trade_service.DeductInventory",
                new=AsyncMock(),
            ) as deduct,
        ):
            messages = await BuildTrade("5x Sol Ring")

        deduct.assert_awaited_once_with([(17, 2)])
        self.assertIn("$5.00", messages[-1])

    async def test_quote_builds_same_report_without_deducting_inventory(self):
        card = {
            "name": "Sol Ring",
            "set": "cmr",
            "set_name": "Commander Legends",
            "collector_number": "335",
            "id": "scryfall-card-id",
        }
        with (
            patch(
                "services.trade_service.GetInventoryForNames",
                new=AsyncMock(return_value=[(17, "Sol Ring", "cmr", 2)]),
            ),
            patch(
                "services.trade_service._EnsureCachedFile",
                side_effect=lambda _name, _ttl, path, _url: path,
            ),
            patch(
                "services.trade_service._LoadScryfallPrintings",
                return_value={("sol ring", "cmr"): [card]},
            ),
            patch(
                "services.trade_service._LoadNormalPrices",
                return_value={"scryfall-card-id": 246},
            ),
            patch(
                "services.trade_service.DeductInventory",
                new=AsyncMock(),
            ) as deduct,
        ):
            messages = await BuildTrade("5x Sol Ring", deduct_inventory=False)

        deduct.assert_not_awaited()
        self.assertIn("$5.00", messages[-1])

    async def test_quote_modal_passes_no_deduction_option(self):
        modal = InventoryTradeModal(object(), deduct_inventory=False)
        modal.cards = SimpleNamespace(component=SimpleNamespace(value="2 Sol Ring"))
        interaction = SimpleNamespace(
            response=SimpleNamespace(defer=AsyncMock()),
            followup=SimpleNamespace(send=AsyncMock()),
        )

        with patch(
            "input_modals.inventory_trade_modal.BuildTrade",
            new=AsyncMock(return_value=["quote"]),
        ) as build:
            await modal.on_submit(interaction)

        build.assert_awaited_once_with("2 Sol Ring", deduct_inventory=False)


class TradeQuoteCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_top_level_command_opens_non_deducting_trade_modal(self):
        cog = TradeQuoteCommand(object())
        interaction = SimpleNamespace(
            response=SimpleNamespace(send_modal=AsyncMock())
        )
        modal = object()

        with patch(
            "commands.trade_quote_command.InventoryTradeModal",
            return_value=modal,
        ) as create_modal:
            await TradeQuoteCommand.TradeQuote.callback(cog, interaction)

        create_modal.assert_called_once_with(cog.bot, deduct_inventory=False)
        interaction.response.send_modal.assert_awaited_once_with(modal)


if __name__ == "__main__":
    unittest.main()
