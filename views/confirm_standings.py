import discord
from tuple_conversions import DataInput

class ConfirmStandings(discord.ui.View):
  def __init__(self, data:DataInput):
    super().__init__(timeout=120)
    self.is_submitted = False
    self.data = data

  @discord.ui.button(label="Confirm & Submit", style=discord.ButtonStyle.success)
  async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.edit_message(content="Submitting data...", view=None)
    for child in self.children: child.disabled = True
    self.stop()
  