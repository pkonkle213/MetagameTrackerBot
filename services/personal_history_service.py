import discord
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from data.personal_history_data import GetStandingsStoreHistory, GetStandingsHubHistory, GetPairingsHubHistory, GetPairingsStoreHistory
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange

def GetPersonalStandingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal standings history for the user"""
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store and not objects.hub:
    raise KnownError('No store or hub found')

  user_id = interaction.user.id
  
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

  if objects.store and not objects.hub:
    data = GetStandingsStoreHistory(user_id, objects.game, objects.format, date_start, date_end, objects.store)
    name = objects.store.store_name if objects.store.store_name else objects.store.discord_name
    headers = ['Date', 'Archetype', 'Wins', 'Losses', 'Draws']
  elif objects.hub and not objects.store:
    data = GetStandingsHubHistory(user_id, objects.game, objects.format, date_start, date_end, objects.hub, objects.region)
    name = objects.hub.hub_name if objects.hub.hub_name else objects.hub.discord_name
    headers = ['Date', 'Store', 'Archetype', 'Wins', 'Losses', 'Draws']
  else:
    raise KnownError('No store or hub found')
    
  if data is None or len(data) == 0:
    return 'No history found.'
  
  title = f'Personal History for {name.title()}'
  
  if not format:
    headers.insert(2, 'Format')
  if not objects.game:
    headers.insert(2, 'Game')

  output = BuildTableOutput(title, headers, data)
  return output

def GetPersonalPairingsHistory(
  interaction: discord.Interaction,
  start_date: str,
  end_date: str):
  """Gets the personal pairings history for the user"""
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store and not objects.hub:
    raise KnownError('No store or hub found')
  
  user_id = interaction.user.id
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

  if objects.hub:
    data = GetPairingsHubHistory(user_id, objects.game, objects.format, date_start, date_end, objects.hub, objects.region)
    name = objects.hub.hub_name if objects.hub.hub_name else objects.hub.discord_name
    headers = ['Date', 'Store', 'Round', 'Your Archetype', "Opponent's Archetype", 'Result']
  elif objects.store:
    data = GetPairingsStoreHistory(user_id, objects.game, objects.format, date_start, date_end, objects.store)
    name = objects.store.store_name if objects.store.store_name else objects.store.discord_name
    headers = ['Date', 'Round', 'Your Archetype', "Opponent's Archetype", 'Result']

  if data is None or len(data) == 0:
    return 'No history found.'
    
  title = f'Personal History for {name.title()}'
  if not objects.format:
    headers.insert(2, 'Format')
  if not objects.game:
    headers.insert(2, 'Game')
    
  output = BuildTableOutput(title, headers, data)
  return output