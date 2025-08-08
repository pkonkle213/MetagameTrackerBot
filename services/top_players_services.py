from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_data import GetInteractionData
from data.player_data import GetTopPlayerData

def GetTopPlayers(interaction:Interaction, start_date, end_date):
  game, format, store, user_id = GetInteractionData(interaction, game=True, format=True, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetTopPlayerData(store, game, format, date_start, date_end)
  title = f'Top Players from {date_start} to {date_end}'
  headers = ['Name', 'Attendance %', 'Win %']
  return data, title, headers