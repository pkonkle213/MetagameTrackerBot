from discord import Interaction, Object, app_commands
from discord.ext import commands

from checks import isPhil
from services.command_error_service import Error
from input_modals.inventory_received_modal import InventoryReceivedModal
from input_modals.inventory_trade_modal import InventoryTradeModal
from services.inventory_service import SyncInventoryFromLatestFile
from settings import BOTGUILDID


class InventoryCommands(commands.GroupCog, name="inventory"):
    """Commands for managing card inventory."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def interaction_check(self, interaction: Interaction) -> bool:
        return isPhil(interaction)

    @app_commands.command(
        name="sync",
        description="Replace inventory from the latest uploaded inventory CSV",
    )
    async def Sync(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        file_name, row_count = await SyncInventoryFromLatestFile()
        await interaction.followup.send(
            f"Inventory replaced with {row_count} rows from `{file_name}`.",
            ephemeral=True,
        )

    @app_commands.command(
        name="trade",
        description="Quote and deduct cards from your inventory",
    )
    async def Trade(self, interaction: Interaction):
        await interaction.response.send_modal(InventoryTradeModal(self.bot))

    @app_commands.command(
        name="received",
        description="Add newly received cards to your inventory",
    )
    async def Received(self, interaction: Interaction):
        await interaction.response.send_modal(InventoryReceivedModal(self.bot))

    @Sync.error
    async def SyncError(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)

    @Trade.error
    async def TradeError(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)

    @Received.error
    async def ReceivedError(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        InventoryCommands(bot), guilds=[Object(id=BOTGUILDID)]
    )
