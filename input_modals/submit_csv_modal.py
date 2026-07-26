import discord
from tuple_conversions import Event, DataConverted
from services.convert_and_save_input import ConvertAndUploadCSV

#TODO: This can handle up to 10 items, let's work with multiple CSV files uploaded to create a loop of data
class SubmitCSVDataModal(discord.ui.Modal, title='Submit Data'):
  def __init__(
    self,
    event: Event,
    file_path: str
  ):
    super().__init__()
    self.file_path = file_path
    self.event = event
    self.converted_data: DataConverted = DataConverted(None, None, None, 0, None, None)
    self.confirm_response = None

    self.csv_data = discord.ui.Label(
      text='CSV File',
      description='Upload up to 10 CSV files for this event.',
      component=discord.ui.FileUpload(
        required=True
      ),
    )
    self.add_item(self.csv_data)

  async def on_submit(self, interaction: discord.Interaction):
    self.interaction = interaction
    await interaction.response.defer(ephemeral=True)
    self.converted_data = ConvertAndUploadCSV(
      self.event,
      self.file_path,
      self.csv_data.component.values[0]
    )
