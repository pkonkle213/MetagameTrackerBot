from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.store_attendance_data import GetStoreAttendance, GetHubAttendance
from settings import DATAGUILDID
from services.command_error_service import KnownError
from tuple_conversions import OutputToBuild

def GetAttendance(interaction:Interaction, start_date:str, end_date:str) -> OutputToBuild:
  objects = GetObjectsFromInteraction(interaction)
  if (not objects.store and not objects.hub) or not objects.game or (not objects.format and not objects.region):
    raise KnownError('No store, hub, game, or region found')
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

  headers = ['Date', 'Event Name', 'Players']
  if not objects.format:
    headers.insert(1, 'Format')
    
  if objects.store:
    data = GetStoreAttendance(
      objects.store,
      objects.game,
      objects.format,
      date_start,
      date_end
    )
    subject = objects.format.format_name.title() if objects.format else objects.game.game_name.title()
    title = f'{subject} attendance from {date_start} to {date_end}'
  elif objects.hub:
    data = GetHubAttendance(
      objects.hub,
      objects.region,
      objects.game,
      objects.format,
      date_start,
      date_end
    )
    title = f'Attendance from {date_start} to {date_end}'
    headers.insert(1, 'Store')
  
  return OutputToBuild(title, headers, data)