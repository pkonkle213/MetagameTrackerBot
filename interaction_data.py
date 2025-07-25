from collections import namedtuple
from custom_errors import KnownError
import discord
import tuple_conversions as tc
import data.interaction_data as db

def GetInteractionData(interaction,
                      game=False,
                      format=False,
                      store=False):
  Requirements = namedtuple("Requirements",["Game","Format","Store"])
  requirements = Requirements(game, format, store)
  raw_data = SplitInteractionData(interaction)
  formatted_data = FormatInteractionData(raw_data, requirements)
  return formatted_data

def SplitInteractionData(interaction):
  discord_guild = interaction.guild
  if discord_guild is None:
    raise KnownError('No guild found')
  discord_id = discord_guild.id
  
  channel = interaction.channel
  if channel is None or not isinstance(channel,discord.TextChannel) or isinstance(channel,discord.GroupChannel):
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
    
  Data = namedtuple("Data",["DiscordId", "CategoryId", "ChannelId", "UserId"])
  return Data(discord_id, category_id, channel_id, user_id)

def GetGame(category_id:int, required):
  game_obj = db.GetGameByMap(category_id)
  if game_obj is None:
    if required:
      raise KnownError('Game not found. Please map a game to this category.')
    else:
      return None
  return tc.ConvertToGame(game_obj)

def GetFormat(game, channel_id:int, required):
  if game is None or not game.HasFormats:
    return None
  format_obj = db.GetFormatByMap(channel_id)
  if format_obj is None:
    if required:
      raise KnownError('Format not found. Please map a format to this channel.')
    else:
      return None
  return tc.ConvertToFormat(format_obj)

def GetStore(discord_id, required=True):
  store_obj = db.GetStoreByDiscord(discord_id)

  if store_obj is None:
    if required:
      raise KnownError('Store not found. Please register your store.')
    else:
      return None
  return tc.ConvertToStore(store_obj[0])

def FormatInteractionData(data, requirements):
  game = GetGame(data.CategoryId, requirements.Game)
  format = GetFormat(game, data.ChannelId, requirements.Format)
  store = GetStore(data.DiscordId, requirements.Store)
  
  Data = namedtuple("Data",["Game","Format","Store","UserId"])
  return Data(game,format,store,data.UserId)
