from services.date_functions import GetToday
import discord

class SubmitDataModal(discord.ui.Modal, title='Submit Data'):
  #Are these necessary?
  #data: str = ''
  #date: str = ''
  is_submitted: bool = False

  date_input = discord.ui.TextInput(
    label='Date',
    style=discord.TextStyle.short,
    placeholder='MM/DD/YYYY',
    default=GetToday().strftime('%m/%d/%Y'),
    required=True,
    max_length=10
  )
  
  message_input = discord.ui.TextInput(
    label='Event Data',
    style=discord.TextStyle.paragraph,
    placeholder='Paste your data here',
    required=True,
    max_length=2000 # Max length for text input
  )
  
  async def on_submit(self, interaction: discord.Interaction):
    self.submitted_message = self.message_input.value
    self.submitted_date = self.date_input.value
    self.is_submitted = True
    await interaction.response.defer()

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False