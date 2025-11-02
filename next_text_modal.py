import discord
from services.date_functions import GetToday

class SubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
  is_submitted = False

  def __init__(self):
    super().__init__()
    today = GetToday()   

    self.date_input = discord.ui.TextInput(
      label='Date of Event',
      style=discord.TextStyle.short,
      placeholder='MM/DD/YYYY',
      default=today.strftime('%m/%d/%Y'),
      required=True,
      max_length=10
    )
    self.add_item(self.date_input)

    self.player_name_input = discord.ui.TextInput(
      label='Player Name',
      style=discord.TextStyle.short,
      placeholder='Player Name',
      required=True,
      max_length=50
    )
    self.add_item(self.player_name_input)
    
    self.archetype_input = discord.ui.TextInput(
       label='Archetype',
       style=discord.TextStyle.short,
       placeholder='Archetype Name',
       required=True,
       max_length=50
    )
    self.add_item(self.archetype_input)

  async def on_submit(self, interaction: discord.Interaction):
    self.submitted_date = self.date_input.value
    self.submitted_player_name = self.player_name_input.value
    self.submitted_archetype = self.archetype_input.value
    self.is_submitted = True
    await interaction.response.defer()

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False