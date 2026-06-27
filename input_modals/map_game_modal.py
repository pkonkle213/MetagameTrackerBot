from custom_errors import KnownError
from data.games_data import GetAllGames, AddGameMap
from services.game_mapper_services import AddStoreGameMap
from tuple_conversions import Game, Store
import discord

class MapGameModal(discord.ui.Modal, title='Map Game'):
  is_submitted = False

  def __init__(self, store:Store):
    super().__init__()
    self.store = store

    self.games = GetAllGames()

    game_options = [discord.SelectOption(label=game.game_name, value=str(game.id)) for game in self.games]

    self.select_game = discord.ui.Label(
      text="Game",
      component=discord.ui.Select(
        options = game_options,
        required=True,
        max_values=1
      )
    )
    self.add_item(self.select_game)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    #if not self.select_game.component:
      #raise Exception("No idea what's going on here")
    selected_game = GetGame(self.select_game.component.values[0], self.games)
    await interaction.response.defer(thinking=False)
    result = AddStoreGameMap(interaction, selected_game)
    await interaction.followup.send(result, ephemeral=True)

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.followup.send(f'Oops! Something went wrong: {error}', ephemeral=True)
    self.is_submitted = False
  
  async def on_timeout(self) -> None:
    self.is_submitted = False

def GetGame(selection:str, games:list[Game]) -> Game:
  for game in games:
    if game.id == int(selection):
      return game
  raise KnownError('Game selected not found')