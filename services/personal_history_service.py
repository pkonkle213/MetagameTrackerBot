import discord
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from data.personal_history_data import GetStandingsHistory, GetPairingsHistory
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange

def GetPersonalStandingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal standings history for the user"""
  store, game, format = GetObjectsFromInteraction(interaction)
  if not store:
    raise KnownError('No Store Found')
    
  user_id = interaction.user.id
  
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetStandingsHistory(user_id, game, format, date_start, date_end, store)
  if data is None or len(data) == 0:
    return 'No history found.'
  name = store.StoreName if store.StoreName else store.DiscordName
  title = f'Personal History for {name.title()}'
  headers = ['Date', 'Archetype', 'Wins', 'Losses', 'Draws']
  if not format:
    headers.insert(1, 'Format')
  if not game:
    headers.insert(1, 'Game')
  if not store:
    headers.insert(1, 'Store Name')
  output = BuildTableOutput(title, headers, data)
  return output

def GetPersonalPairingsHistory(
  interaction: discord.Interaction,
  start_date: str,
  end_date: str):
  """Gets the personal pairings history for the user"""
  store, game, format = GetObjectsFromInteraction(interaction)
  if not store:
    raise KnownError('No Store Found')
  user_id = interaction.user.id
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetPairingsHistory(user_id, game, format, date_start, date_end, store)
  if data is None or len(data) == 0:
    return 'No history found.'
  name = store.StoreName if store.StoreName else store.DiscordName
  title = f'Personal History for {name.title()}'
  headers = ['Date', 'Round', 'Your Archetype', "Opponent's Archetype", 'Result']
  if not format:
    headers.insert(1, 'Format')
  if not game:
    headers.insert(1, 'Game')
  if not store:
    headers.insert(1, 'Store Name')
  output = BuildTableOutput(title, headers, data)
  return output