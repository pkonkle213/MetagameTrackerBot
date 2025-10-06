from services.date_functions import GetToday
import discord

class SubmitDataModal(discord.ui.Modal, title='Submit Data'):
  is_submitted = False
  
  def __init__(self):
    super().__init__()
    today = GetToday()

    self.date_input = discord.ui.TextInput(
      label='Date',
      style=discord.TextStyle.short,
      placeholder='MM/DD/YYYY',
      default=today.strftime('%m/%d/%Y'),
      required=True,
      max_length=10
    )
    self.add_item(self.date_input)

    #TODO: This needs to be tested
    """
    self.is_event_complete = discord.ui.Select(
      options=[
        discord.SelectOption(label='Yes', value='True'),
        discord.SelectOption(label='No', value='False')
      ],
      placeholder='Is the event complete?',
      min_values=1,
      max_values=1
    )
    self.add_item(self.is_event_complete)
    """
  
    self.message_input = discord.ui.TextInput(
      label='Event Data',
      style=discord.TextStyle.paragraph,
      placeholder='Paste your data here',
      required=True,
      max_length=2000 # Max length for text input
    )
    self.add_item(self.message_input)
  
  async def on_submit(self, interaction: discord.Interaction):
    self.submitted_message = self.message_input.value
    self.submitted_date = self.date_input.value
    #self.submitted_is_event_complete = self.is_event_complete.values[0]
    self.is_submitted = True
    await interaction.response.defer()

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False

  async def on_timeout(self) -> None:
    self.is_submitted = False