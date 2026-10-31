import discord

from services.command_error_service import Error
from services.trade_service import BuildTrade


class InventoryTradeModal(discord.ui.Modal, title="Trade Inventory"):
    def __init__(self, bot: discord.Client, deduct_inventory: bool = True):
        super().__init__()
        self.bot = bot
        self.deduct_inventory = deduct_inventory
        self.cards = discord.ui.Label(
            text="Cards to trade",
            component=discord.ui.TextInput(
                placeholder="4 Card Name\n2x Another Card\n1 - A Third Card",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=4000,
            ),
        )
        self.add_item(self.cards)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            messages = await BuildTrade(
                self.cards.component.value,
                deduct_inventory=self.deduct_inventory,
            )
            for message in messages:
                await interaction.followup.send(message, ephemeral=True)
        except Exception as error:
            await Error(self.bot, interaction, error)
