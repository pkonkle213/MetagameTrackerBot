from collections import namedtuple
import discord
import tuple_conversions as tc
import database_connection as db

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
    raise Exception('No guild found')
  discord_id = discord_guild.id
  
  channel = interaction.channel
  if channel is None or not isinstance(channel,discord.TextChannel) or isinstance(channel,discord.GroupChannel):
    raise Exception('No channel found')

  channel_id = channel.id
  
  category = channel.category
  if category is None:
    raise Exception('No category found')
  category_id = category.id
  
  user_id = -1
  if isinstance(interaction, discord.Interaction):
    user_id = interaction.user.id
  if isinstance(interaction, discord.Message):
    user_id = interaction.author.id

  if user_id == -1:
    raise Exception('No user found!?')
  Data = namedtuple("Data",["DiscordId", "CategoryId", "ChannelId", "UserId"])
  return Data(discord_id, category_id, channel_id, user_id)

def GetGame(category_id:int, required):
  game_obj = db.GetGameByMap(category_id)
  if game_obj is None:
    if required:
      raise Exception('Game not found')
    else:
      return None
  return tc.ConvertToGame(game_obj)

def GetFormat(game, channel_id:int, required):
  if game is None or not game.HasFormats:
    return None
  format_obj = db.GetFormatByMap(channel_id)
  if format_obj is None:
    if required:
      raise Exception('Format not found')
    else:
      return None
  return tc.ConvertToFormat(format_obj)

def GetStore(discord_id, required=True):
  store_obj = db.GetStores(discord_id=discord_id)
  if store_obj is None:
    if required:
      raise Exception('Store not found')
    else:
      return None
  return tc.ConvertToStore(store_obj[0])

def FormatInteractionData(data, requirements):
  game = GetGame(data.CategoryId, requirements.Game)
  format = GetFormat(game, data.ChannelId, requirements.Format)
  store = GetStore(data.DiscordId, requirements.Store)

  Data = namedtuple("Data",["Game","Format","Store","UserId"])
  return Data(game,format,store,data.UserId)
