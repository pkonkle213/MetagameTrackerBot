import discord
from tuple_conversions import ViewButtonEnum


class ConfirmEvent(discord.ui.View):
    def __init__(self, next_modal: discord.ui.Modal | None = None):
        super().__init__(timeout=120)
        self.action = None
        self.interaction: discord.Interaction | None = None
        self.next_modal = next_modal

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.action = ViewButtonEnum.Cancel.value
        self.interaction = interaction
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def approve_event(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.action = ViewButtonEnum.Continue.value
        self.interaction = interaction
        if self.next_modal:
            await interaction.response.send_modal(self.next_modal)
        else:
            await interaction.response.defer()
        self.stop()
