from collections import namedtuple
import discord
import tuple_conversions as tc
import database_connection as db

def GetInteractionData(interaction:discord.Interaction):
  raw_data = SplitInteractionData(interaction)
  data = FormatInteractionData(raw_data)
  return data

def SplitInteractionData(interaction:discord.Interaction):
  discord_guild = interaction.guild
  if discord_guild is None:
    raise Exception('No guild found')
  discord_id = discord_guild.id
  
  channel = interaction.channel
  print('Channel type:',type(channel))
  if channel is None or not isinstance(channel,discord.TextChannel) or isinstance(channel,discord.GroupChannel):
    raise Exception('No channel found')

  format_name = channel.name

  category = channel.category
  if category is None:
    raise Exception('No category found')
  game_name = category.name
  
  user_id = interaction.user.id
  Data = namedtuple("Data",["DiscordId","GameName","FormatName","UserId"])
  return Data(discord_id,game_name,format_name,user_id)

def GetGame(discord_id, game_name):
  game_obj = db.GetGame(discord_id, game_name)
  if game_obj is None:
    raise Exception('Game not found')
  return tc.ConvertToGame(game_obj)

def GetFormat(discord_id, game, format_name):
  if not game.HasFormats:
    return None
  format_obj = db.GetFormat(game.ID, format_name)
  if format_obj is None:
    raise Exception('Format not found')
  return tc.ConvertToFormat(format_obj)

def GetStore(discord_id):
  store_obj = db.GetStores(discord_id=discord_id)
  if store_obj is None:
    raise Exception('Store not found')
  return tc.ConvertToStore(store_obj[0])

#TODO: For some functions, format and game may be None and that's okay
def FormatInteractionData(data):
  game = GetGame(data.DiscordId, data.GameName)
  format = GetFormat(data.DiscordId, game, data.FormatName)
  store = GetStore(data.DiscordId)

  Data = namedtuple("Data",["Game","Format","Store","UserId"])
  return Data(game,format,store,data.UserId)