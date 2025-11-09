from discord import Interaction, TextChannel
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from data.games_data import AddGameMap, GetAllGames
from tuple_conversions import Game

def AddStoreGameMap(interaction:Interaction,
                    chosen_game: Game):
  interaction_objs = GetObjectsFromInteraction(interaction,
                                                    store=True)
  channel = interaction.channel
  if not isinstance(channel, TextChannel):
    raise KnownError('Cannot map a game to a category that does not have text channels')
  category = channel.category
  if category is None:
    raise KnownError('Must map a game to a category')
  category_id = category.id

  rows = AddGameMap(interaction_objs.Store.DiscordId, chosen_game[0], category_id)
  if rows is None:
    return 'Unable to add game map'
  return f'Success! This category ({category.name}) is now mapped to {chosen_game[1].title()}'

def GetGameOptions():
  return GetAllGames()