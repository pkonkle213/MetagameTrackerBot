from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.player_data import GetTopPlayerData
from services.command_error_service import KnownError

def GetTopPlayers(interaction: Interaction, start_date, end_date):
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game:
    raise KnownError('Unable to find store or game')
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
  data = GetTopPlayerData(objects.store, objects.game, objects.format, date_start, date_end)
  title = f'Top Players from {date_start.strftime('%B %d')} to {date_end.strftime('%B %d')}'
  headers = ['Name', 'Points', 'Win %']
  return data, title, headers
