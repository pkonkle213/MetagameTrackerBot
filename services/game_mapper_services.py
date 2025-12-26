from replit import db
from discord import Interaction, TextChannel
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from data.games_data import AddGameMap, GetAllGames
from tuple_conversions import Game

def AddStoreGameMap(interaction:Interaction,
                    chosen_game: Game):
  store = GetObjectsFromInteraction(interaction)[0]
  channel = interaction.channel
  if not isinstance(channel, TextChannel):
    raise KnownError('Cannot map a game to a category that does not have text channels')
  category = channel.category
  if category is None:
    raise KnownError('Must map a game to a category')
  category_id = category.id

  rows = AddGameMap(store.DiscordId, chosen_game[0], category_id)
  if rows is None:
    return 'Unable to add game map'
  return f'Success! This category ({category.name}) is now mapped to {chosen_game[1].title()}'

#TODO: If another category is mapped to the same game, this means that both categories will be mapped to the same game. This is not ideal.
def AddGameRKV(interaction:Interaction, game:Game) -> bool:
  try:
    discord_id = interaction.guild.id
    category_id = interaction.channel.category_id
    map = {
            f'{category_id}':
            {
              'game': game,
              'formats': {}
            }
          }
    db[f'{discord_id}'] = map
    return True
  except Exception as e:
    print('Error adding game to RKV:', e)
    return False
  

def GetGameOptions():
  return GetAllGames()