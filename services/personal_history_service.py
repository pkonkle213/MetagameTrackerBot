import discord
from interaction_objects import GetObjectsFromInteraction
from data.personal_history_data import GetStandingsHistory, GetPairingsHistory
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange

def GetPersonalStandingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal standings history for the user"""
  game, format, store, user_id = GetObjectsFromInteraction(interaction, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetStandingsHistory(user_id, game, format, date_start, date_end, store)
  if data is None:
    return 'No history found.'
  title = f'Personal History for {store.StoreName.title()}'
  headers = ['Date', 'Archetype', 'Wins', 'Losses', 'Draws']
  if not format:
    headers.insert(1, 'Format')
  if not game:
    headers.insert(1, 'Game')
  if not store:
    headers.insert(1, 'Store Name')
  output = BuildTableOutput(title, headers, data)
  return output

def GetPersonalPairingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal pairings history for the user"""
  game, format, store, user_id = GetObjectsFromInteraction(interaction, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetPairingsHistory(user_id, game, format, date_start, date_end, store)
  if data is None:
    return 'No history found.'
  title = f'Personal History for {store.StoreName.title()}'
  headers = ['Date', 'Round', 'Archetype', 'Result']
  if not format:
    headers.insert(1, 'Format')
  if not game:
    headers.insert(1, 'Game')
  if not store:
    headers.insert(1, 'Store Name')
  output = BuildTableOutput(title, headers, data)
  return output