from collections import namedtuple
from typing import NamedTuple
from custom_errors import KnownError
import discord
import data.interaction_data as db
from tuple_conversions import Game, Data
from models.game import Game
from models.format import Format
from models.store import Store

class Requirements(NamedTuple):
  Game:bool
  Format:bool
  Store:bool

def GetObjectsFromInteraction(interaction: discord.Interaction,
                              game:bool = False,
                              format:bool = False,
                              store:bool = False):
  """Gets the game, format, store, and user_id from the interaction"""
  requirements = Requirements(game, format, store)
  discord_id, category_id, channel_id, user_id = SplitInteractionData(interaction)
  formatted_data = FormatInteractionData(discord_id, category_id, channel_id, user_id, requirements)
  return formatted_data


def SplitInteractionData(interaction: discord.Interaction):
  """Converts the interaction into appropriate ids
  
  Parameters:
    interaction (discord.Interaction): The interaction to split"""
  discord_guild = interaction.guild
  if discord_guild is None:
    raise KnownError('No guild found')
  discord_id = discord_guild.id

  channel = interaction.channel
  if channel is None or not isinstance(channel, discord.TextChannel) or isinstance(channel, discord.GroupChannel):
    raise KnownError('No channel found.')

  channel_id = channel.id

  category = channel.category
  if category is None:
    raise KnownError('No category found.')
  category_id = category.id

  user_id = -1
  user_id = interaction.user.id
  
  return discord_id, category_id, channel_id, user_id

def GetGame(category_id: int,
            required: bool) -> Game:
  """Returns the game mapped to the given category_id
  
  Parameters:
    category_id (int): The category_id mapped to the game
    required (bool): Whether or not the game is required"""
  game = db.GetGameByMap(category_id)
  if game is None and required:
    raise KnownError('Game not found. Please map a game to this category.')
  return game

def GetFormat(game: Game, channel_id: int, required: bool) -> Format:
  """Returns the format mapped to the given channel_id
  
  Parameters:
    game (Game): The game to get the format for
    channel_id (int): The channel_id mapped to the format
    required (bool): Whether or not the format is required"""
  format = db.GetFormatByMap(channel_id)
  if format is None and required:
    raise KnownError('Format not found. Please map a format to this channel.')
  return format

def GetStore(discord_id: int,
             required: bool = True) -> Store:
  """Returns the store mapped to the given discord_id
  
  Parameters:
    discord_id (int): The discord_id to get the store for
    required (bool): Whether or not the store is required"""
  store = db.GetStoreByDiscord(discord_id)

  if store is None and required:
    raise KnownError('Store not found. Please register your store.')
  return store

def FormatInteractionData(discord_id:int, category_id:int, channel_id:int, user_id:int, requirements:Requirements) -> tuple[Game, Format, Store, int]:
  """Formats the interaction data into the appropriate objects"""
  game = GetGame(data.CategoryId, requirements.Game)
  format = GetFormat(game, data.ChannelId, requirements.Format)
  store = GetStore(data.DiscordId, requirements.Store)
  return Data(game, format, store, data.UserId)
