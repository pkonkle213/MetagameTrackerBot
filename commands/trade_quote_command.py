from discord import Interaction, app_commands
from discord.ext import commands

from checks import isPhil
from input_modals.inventory_trade_modal import InventoryTradeModal
from services.command_error_service import Error


class TradeQuoteCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="trade_quote",
        description="Quote inventory cards without deducting stock",
    )
    @app_commands.guild_only()
    @app_commands.check(isPhil)
    async def TradeQuote(self, interaction: Interaction):
        await interaction.response.send_modal(
            InventoryTradeModal(self.bot, deduct_inventory=False)
        )

    @TradeQuote.error
    async def TradeQuoteError(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(TradeQuoteCommand(bot))
