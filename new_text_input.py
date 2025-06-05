import discord

class ClaimCheckModal(discord.ui.Modal, title='Claim Check'):
  # This attribute will store the message if the modal is submitted
  submitted_message: str = ''
  # This attribute indicates if the modal was submitted or dismissed/timed out
  is_submitted: bool = False

  message_input = discord.ui.TextInput(
      label='Message',
      style=discord.TextStyle.paragraph,
      default='Is this it?',
      required=True,
      max_length=2000 # Max length for text input
  )

  def __init__(self):
      super().__init__()
      # Add the text input to the modal
      self.add_item(self.message_input)

  async def on_submit(self, interaction: discord.Interaction):
      # When submitted, store the value and set the flag
      self.submitted_message = self.message_input.value
      self.is_submitted = True
      # Acknowledge the interaction, but don't send a full response yet.
      # This prevents the "interaction failed" message from Discord.
      await interaction.response.defer()

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
      # Handle any errors during modal submission
      await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
      self.is_submitted = False # Indicate that submission failed

  async def on_timeout(self) -> None:
      # Handle when the user doesn't submit the modal in time
      # No interaction object here, so no direct response to the user.
      # The calling command will handle the lack of submission based on self.is_submitted
      self.is_submitted = False