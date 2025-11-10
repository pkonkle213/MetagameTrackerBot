from services.date_functions import GetToday
import discord

class SubmitDataModal(discord.ui.Modal, title='Submit Data'):
  is_submitted = False
  
  def __init__(self):
    super().__init__()
    today = GetToday()

    self.date_input = discord.ui.Label(
      text="Event Date",
      component=discord.ui.TextInput(
        placeholder='MM/DD/YYYY',
        default=today.strftime('%m/%d/%Y'),
        required=True,
        max_length=10
      )
    )
    self.add_item(self.date_input)

    self.round_input = discord.ui.Label(
      text="Round Number",
      component=discord.ui.TextInput(
        placeholder='Round Number',
        required=False,
        max_length=3
      )
    )
    self.add_item(self.round_input)
  
    self.message_input = discord.ui.Label(
      text="Event Data",
      component=discord.ui.TextInput(
        style=discord.TextStyle.paragraph,
        placeholder='Paste your data here',
        required=True,
        max_length=2000 # Max length for text input
      )
    )
    self.add_item(self.message_input)

  async def on_submit(self, interaction: discord.Interaction):
    self.submitted_message = self.message_input.component.value
    self.submitted_date = self.date_input.component.value
    self.submitted_round = self.round_input.component.value
    self.is_submitted = True
    await interaction.response.defer()

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False