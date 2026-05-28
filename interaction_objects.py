from custom_errors import KnownError
import discord
import data.interaction_data as db
from tuple_conversions import Game, Format, Store, InteractionObjects, Hub, Region

def GetObjectsFromInteraction(interaction: discord.Interaction) -> InteractionObjects:
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

  store = GetStore(discord_id)
  hub = GetHub(discord_id)
  
  if store:
    region = DetermineRegion(store, 0)
    game = GetGameForStore(category_id, discord_id)
    format = GetFormatForStore(game, channel_id, discord_id)
  elif hub:
    region = DetermineRegion(hub, channel_id)
    game = GetGameForHub(category_id, discord_id)
    format = GetFormatForHub(channel_id, discord_id)
  else:
    raise KnownError("You lied! There's no store or hub found.")

  print('Results:')
  print('Store:', store)
  print('Hub:', hub)
  print('Region:', region)
  print('Game:', game)
  print('Format:', format)
  
  return InteractionObjects(store, hub, region, game, format)

def DetermineRegion(hub: Hub | Store, channel_id:int) -> Region | None:
  if hub.region_id:
    return Region(hub.region_id, '')

  region = db.GetRegion(hub.discord_id, channel_id)
  return region

def GetHub(discord_id: int) -> Hub | None:
  """Returns the hub mapped to the given discord_id
  
  Parameters:
    discord_id (int): The discord_id to get the hub for"""
  hub = db.GetHubByDiscord(discord_id)
  return hub

def GetGameForStore(category_id: int, discord_id: int) -> Game | None:
  """Returns the game mapped to the given category_id
  
  Parameters:
    category_id (int): The category_id mapped to the game"""
  game = db.GetGameByMap(category_id, discord_id)
 
  return game

def GetGameForHub(category_id: int, discord_id: int) -> Game | None:
  """Returns the game mapped to the given category_id or determined by the discord's game_lock"""
  game = db.GetGameByHub(category_id, discord_id)

  return game

def GetFormatForHub(
  channel_id: int,
  discord_id: int
) -> Format | None:
  format = db.GetFormatByMap(channel_id, discord_id)
  return format

def GetFormatForStore(
  game: Game | None,
  channel_id: int,
  discord_id: int
) -> Format | None:
  """Returns the format mapped to the given channel_id
  
  Parameters:
    game (Game): The game to get the format for
    channel_id (int): The channel_id mapped to the format
    required (bool): Whether or not the format is required"""
  if game is None:
    return None
  format = db.GetFormatByMap(channel_id, discord_id)
  return format

def GetStore(discord_id: int) -> Store | None:
  """Returns the store mapped to the given discord_id
  
  Parameters:
    discord_id (int): The discord_id to get the store for"""
  store = db.GetStoreByDiscord(discord_id)
  
  return store
