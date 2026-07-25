import discord
from tuple_conversions import Event, Store, Game, Format, DataConverted
from services.convert_and_save_input import ConvertAndUploadCSV


class MockAttachment:
  """Mimics discord.Attachment so ConvertAndUploadCSV can be called with pasted CSV text."""

  def __init__(self, filename: str, content: str):
    self.filename = filename
    self._content = content.encode('utf-8')

  async def read(self) -> bytes:
    return self._content


class SubmitCSVModal(discord.ui.Modal, title='Submit CSV Data'):
  def __init__(
    self,
    event: Event,
    store: Store,
    game: Game,
    format: Format
  ):
    super().__init__()
    self.event = event
    self.store = store
    self.game = game
    self.format = format
    self.converted_data: DataConverted = DataConverted(None, None, None, 0, None, None)
    self.confirm_response = None
    self.interaction: discord.Interaction | None = None

    self.filename_input = discord.ui.Label(
      text="CSV Filename",
      component=discord.ui.TextInput(
        placeholder="e.g. STANDINGS-0-12345-0-0.csv",
        required=True,
        max_length=100
      )
    )
    self.add_item(self.filename_input)

    self.csv_data = discord.ui.Label(
      text="CSV Data",
      component=discord.ui.TextInput(
        placeholder="Paste your CSV content here",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
        min_length=10
      )
    )
    self.add_item(self.csv_data)

  async def on_submit(self, interaction: discord.Interaction):
    self.interaction = interaction
    await interaction.response.defer(ephemeral=True)
    attachment = MockAttachment(
      self.filename_input.component.value,
      self.csv_data.component.value
    )
    self.converted_data = await ConvertAndUploadCSV(
      self.event,
      attachment,
      self.store,
      self.game,
      self.format
    )
