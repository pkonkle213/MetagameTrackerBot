from collections import namedtuple
from settings import TESTGUILDID
from custom_errors import KnownError
from services.date_functions import ConvertToDate
import discord
import data.interaction_data as db
from tuple_conversions import Game, Data, Format, Store


def GetObjectsFromInteraction(
    interaction: discord.Interaction
) -> tuple[Store | None, Game | None, Format | None]:
  """Gets the game, format, store, and user_id from the interaction"""
  discord_id = interaction.guild_id
  if not discord_id:
    raise KnownError('No guild found')
  if not isinstance(interaction.channel, discord.TextChannel):
    raise KnownError('No channel found.')
  category_id = interaction.channel.category_id
  if not category_id:
    raise KnownError('No category found.')
  channel_id = interaction.channel_id
  if not channel_id:
    raise KnownError('No channel found.')

  store, game, format = db.GetInteractionDetails(discord_id, category_id,
                                                 channel_id)

  """if store and store.DiscordId == TESTGUILDID:
    store = Store(1210746744602890310, 'Test Guild', 'Test Store',
                  505548744444477441, 'Phil', '123 Street', True, True, 'Ohio',
                  'Cbus', False)
    game = Game(1, 'Magic')
    format = Format(1, 'Pauper', ConvertToDate('1/1/2020'), False)"""
  return store, game, format


def SplitInteractionData(interaction: discord.Interaction):
  """Converts the interaction into appropriate ids
  
  Parameters:
    interaction (discord.Interaction): The interaction to split"""
  discord_guild = interaction.guild
  if discord_guild is None:
    raise KnownError('No guild found')
  discord_id = discord_guild.id

  channel = interaction.channel
  if channel is None or not isinstance(channel,
                                       discord.TextChannel) or isinstance(
                                           channel, discord.GroupChannel):
    raise KnownError('No channel found.')

  channel_id = channel.id

  category = channel.category
  if category is None:
    raise KnownError('No category found.')
  category_id = category.id

  user_id = -1
  if isinstance(interaction, discord.Interaction):
    user_id = interaction.user.id
  elif isinstance(interaction, discord.Message):
    user_id = interaction.author.id
  else:
    raise KnownError('No user found!?')

  Data = namedtuple("Data", ["DiscordId", "CategoryId", "ChannelId", "UserId"])
  return Data(discord_id, category_id, channel_id, user_id)


def GetGame(category_id: int, required: bool):
  """Returns the game mapped to the given category_id
  
  Parameters:
    category_id (int): The category_id mapped to the game
    required (bool): Whether or not the game is required"""
  game = db.GetGameByMap(category_id)
  if game is None and required:
    raise KnownError('Game not found. Please map a game to this category.')
  return game


def GetFormat(game: Game | None, channel_id: int,
              required: bool) -> Format | None:
  """Returns the format mapped to the given channel_id
  
  Parameters:
    game (Game): The game to get the format for
    channel_id (int): The channel_id mapped to the format
    required (bool): Whether or not the format is required"""
  if game is None:
    return None
  format = db.GetFormatByMap(channel_id)
  if format is None and required:
    raise KnownError('Format not found. Please map a format to this channel.')
  return format


def GetStore(discord_id: int, required: bool = True):
  """Returns the store mapped to the given discord_id
  
  Parameters:
    discord_id (int): The discord_id to get the store for
    required (bool): Whether or not the store is required"""
  store = db.GetStoreByDiscord(discord_id)

  if store is None and required:
    raise KnownError('Store not found. Please register your store.')
  return store


def FormatInteractionData(data, requirements):
  """Formats the interaction data into the appropriate objects"""
  game = GetGame(data.CategoryId, requirements.Game)
  format = GetFormat(game, data.ChannelId, requirements.Format)
  store = GetStore(data.DiscordId, requirements.Store)
  return Data(game, format, store, data.UserId)
