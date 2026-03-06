from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.store_attendance_data import GetAttendance
from settings import DATAGUILDID
from services.command_error_service import KnownError

def GetStoreAttendance(interaction:Interaction, start_date, end_date):
  store, game, format = GetObjectsFromInteraction(interaction)
  if not store or not game:
    raise KnownError('No store or game found')
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  
  data = GetAttendance(store,
                       game,
                       format,
                       date_start,
                       date_end)
  subject = format.FormatName.title() if format else game.GameName.title()
  title = f'{subject} attendance from {date_start} to {date_end}'
  headers = ['Date', 'Event Name', 'Players']
  if not format:
    headers.insert(1, 'Format')
  if store.DiscordId == DATAGUILDID:
    headers.insert(1, 'Store')
  
  return (data, title, headers)