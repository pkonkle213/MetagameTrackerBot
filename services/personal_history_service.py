import discord
from interaction_data import GetInteractionData
from data.personal_history_data import GetPersonalHistory
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange

def GetPersonalStandingsHistory(interaction: discord.Interaction, start_date: str, end_date: str):
  """Gets the personal standings history for the user"""
  game, format, store, user_id = GetInteractionData(interaction, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetPersonalHistory(user_id, game, format, date_start, date_end, store)
  if data is None:
    return None
  title = f'Personal History for {store.StoreName.title()}'
  headers = ['Date', 'Archetype', 'Wins', 'Losses', 'Draws']
  if not format:
    headers.insert(1, 'Format')
  if not game:
    headers.insert(1, 'Game')
  output = BuildTableOutput(title, headers, data)
  return output