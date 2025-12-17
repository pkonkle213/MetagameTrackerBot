from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.store_attendance_data import GetAttendance
from settings import DATAGUILDID

def GetStoreAttendance(interaction:Interaction, start_date, end_date):
  game, format, store, userId = GetObjectsFromInteraction(interaction,
                                                   game=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  
  data = GetAttendance(store,
                       game,
                       format,
                       date_start,
                       date_end)
  subject = format.Name.title() if format else game.Name.title()
  title = f'{subject} attendance from {date_start} to {date_end}'
  headers = ['Date', 'Players']
  if not format:
    headers.insert(1, 'Format')
  if store.DiscordId == DATAGUILDID:
    headers.insert(1, 'Store')
  
  return (data, title, headers)