from tuple_conversions import Format, Game, Store
from services.command_error_service import KnownError
from data.formats_data import GetFormatsByGameId
from services.formats_services import AddStoreFormatMap
import discord

class MapFormatModal(discord.ui.Modal, title='Map Format'):
  def __init__(self, store:Store, game:Game):
    super().__init__()
    self.store = store
    self.game = game

    self.formats = GetFormatsByGameId(game)
    format_options = [discord.SelectOption(label=format.format_name, value=str(format.id)) for format in self.formats]

    self.select_format = discord.ui.Label(
      text="Format",
      component=discord.ui.Select(
        options = format_options,
        required=True,
        max_values=1
      )
    )
    self.add_item(self.select_format)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    selected_format = GetFormat(self.select_format.component.values[0], self.formats)
    await interaction.response.defer(thinking=False)
    result = await AddStoreFormatMap(interaction, selected_format)
    await interaction.followup.send(result,ephemeral=True)

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
     await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    
def GetFormat(selection:str, formats:list[Format]) -> Format:
  for format in formats:
     if format.id == int(selection):
       return format
  raise KnownError('Format selected not found')