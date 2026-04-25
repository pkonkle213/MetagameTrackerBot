import discord
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from data.personal_history_data import GetStandingsHistory, GetPairingsHistory
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange

def GetPersonalStandingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal standings history for the user"""
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store:
    raise KnownError('No Store Found')

  user_id = interaction.user.id
  
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
  data = GetStandingsHistory(user_id, objects.game, objects.format, date_start, date_end, objects.store)
  if data is None or len(data) == 0:
    return 'No history found.'
  name = objects.store.store_name if objects.store.store_name else objects.store.discord_name
  title = f'Personal History for {name.title()}'
  headers = ['Date', 'Archetype', 'Wins', 'Losses', 'Draws']
  if not format:
    headers.insert(1, 'Format')
  if not objects.game:
    headers.insert(1, 'Game')
  if not objects.store:
    headers.insert(1, 'Store Name')
  output = BuildTableOutput(title, headers, data)
  return output

def GetPersonalPairingsHistory(
  interaction: discord.Interaction,
  start_date: str,
  end_date: str):
  """Gets the personal pairings history for the user"""
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store:
    raise KnownError('No Store Found')
  
  user_id = interaction.user.id
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
  data = GetPairingsHistory(user_id, objects.game, objects.format, date_start, date_end, objects.store)
  if data is None or len(data) == 0:
    return 'No history found.'
  name = objects.store.store_name if objects.store.store_name else objects.store.discord_name
  title = f'Personal History for {name.title()}'
  headers = ['Date', 'Round', 'Your Archetype', "Opponent's Archetype", 'Result']
  if not objects.format:
    headers.insert(1, 'Format')
  if not objects.game:
    headers.insert(1, 'Game')
  if not objects.store:
    headers.insert(1, 'Store Name')
  output = BuildTableOutput(title, headers, data)
  return output