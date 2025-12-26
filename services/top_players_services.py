from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.player_data import GetTopPlayerData


def GetTopPlayers(interaction: Interaction, start_date, end_date):
  store, game, format = GetObjectsFromInteraction(interaction)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetTopPlayerData(store, game, format, date_start, date_end)
  title = f'Top Players from {date_start} to {date_end}'
  headers = ['Name', 'Attendance %', 'Win %']
  return data, title, headers
