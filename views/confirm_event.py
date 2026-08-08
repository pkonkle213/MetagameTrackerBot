import discord
from tuple_conversions import ViewButtonEnum


class ConfirmEvent(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.action = None
        self.interaction: discord.Interaction | None = None

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.action = ViewButtonEnum.Cancel.value
        self.interaction = interaction
        self.stop()

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def approve_event(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.action = ViewButtonEnum.Continue.value
        self.interaction = interaction
        self.stop()
