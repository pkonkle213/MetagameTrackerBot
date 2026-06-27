import discord
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from data.personal_history_data import GetStandingsHistory, GetPairingsHistory
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange

def GetPersonalStandingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal standings history for the user"""
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store and not objects.hub:
    raise KnownError('No store or hub found')

  user_id = interaction.user.id
  
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

  data = GetStandingsHistory(user_id, objects.store, objects.hub, objects.region, objects.game, objects.format, date_start, date_end)
  headers = ['Date', 'Archetype', 'Wins', 'Losses', 'Draws']
  
  if objects.hub:
    name = objects.hub.hub_name if objects.hub.hub_name else objects.hub.discord_name
    headers.insert(1, 'Store')
  elif objects.store:
    name = objects.store.store_name if objects.store.store_name else objects.store.discord_name
      
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

  data = GetPairingsHistory(user_id, objects.store, objects.hub, objects.region, objects.game, objects.format, date_start, date_end)
  headers = ['Date', 'Round', 'Your Archetype', "Opponent's Archetype", 'Result']

  name = 'You'
  if objects.hub:
    name = objects.hub.hub_name if objects.hub.hub_name else objects.hub.discord_name
    headers.insert(1, 'Store')
  elif objects.store:
    name = objects.store.store_name if objects.store.store_name else objects.store.discord_name

  if data is None or len(data) == 0:
    return 'No history found.'

  title = f'Personal History for {name.title()}'
  if not objects.format:
    headers.insert(2, 'Format')
  if not objects.game:
    headers.insert(2, 'Game')

  output = BuildTableOutput(title, headers, data)
  return output
