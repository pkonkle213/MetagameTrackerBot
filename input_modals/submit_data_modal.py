import discord
from tuple_conversions import Event, DataConverted
from services.convert_and_save_input import ConvertAndUploadMessage


class SubmitManualDataModal(discord.ui.Modal, title='Submit Data'):
  def __init__(
    self,
    event: Event,
    file_path: str
  ):
    super().__init__()
    self.file_path = file_path
    self.event = event
    self.converted_data:DataConverted = DataConverted(None, None, None, 0, None, None)
    self.confirm_response = None
  
    self.manual_data = discord.ui.Label(
      text="Event Data",
      component=discord.ui.TextInput(
        placeholder="Paste your data here",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000,
        min_length=10)
    )
    self.add_item(self.manual_data)

  async def on_submit(self, interaction: discord.Interaction):
    self.converted_data = ConvertAndUploadMessage(
      self.event,
      self.file_path,
      self.message_input.component.value
    )
