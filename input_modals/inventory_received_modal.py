import discord

from services.command_error_service import Error
from services.inventory_service import ReceiveInventory


class InventoryReceivedModal(discord.ui.Modal, title="Receive Inventory"):
    def __init__(self, bot: discord.Client):
        super().__init__()
        self.bot = bot
        self.cards = discord.ui.Label(
            text="Cards received",
            description="Use one line per entry: quantity card name - card edition",
            component=discord.ui.TextInput(
                placeholder="2 Sol Ring - CMR\n4 Island - DMU",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=4000,
            ),
        )
        self.add_item(self.cards)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            updated_count, inserted_count = await ReceiveInventory(
                self.cards.component.value
            )
            await interaction.followup.send(
                f"Inventory received: {updated_count} existing entries updated; "
                f"{inserted_count} new entries added.",
                ephemeral=True,
            )
        except Exception as error:
            await Error(self.bot, interaction, error)
