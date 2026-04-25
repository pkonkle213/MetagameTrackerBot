from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.store_attendance_data import GetAttendance
from settings import DATAGUILDID
from services.command_error_service import KnownError

def GetStoreAttendance(interaction:Interaction, start_date, end_date):
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game:
    raise KnownError('No store or game found')
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
  
  data = GetAttendance(objects.store,
                       objects.game,
                       objects.format,
                       date_start,
                       date_end)
  subject = objects.format.format_name.title() if objects.format else objects.game.game_name.title()
  title = f'{subject} attendance from {date_start} to {date_end}'
  headers = ['Date', 'Event Name', 'Players']
  if not format:
    headers.insert(1, 'Format')
  if objects.store.discord_id == DATAGUILDID:
    headers.insert(1, 'Store')
  
  return (data, title, headers)