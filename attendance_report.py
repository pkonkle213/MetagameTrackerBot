from discord import Interaction
from date_functions.date_functions import BuildDateRange
from interaction_data import GetInteractionData
from database_connection import GetAttendance
from settings import DATAGUILDID

#TODO: Make this more flexible to allow for multiple stores (DATAGUILD)
def GetStoreAttendance(interaction:Interaction, start_date, end_date):
  game, format, store, userId = GetInteractionData(interaction,
    game=True,
    store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)

  data = GetAttendance(store,
                       game,
                       format,
                       date_start,
                       date_end)
  subject = format.FormatName.title() if game.HasFormats and format is not None else game.Name.title()
  title = f'{subject} attendance from {date_start} to {date_end}'
  headers = ['Date', 'Players']
  if not format:
    headers.insert(1, 'Format')
  if not store:
    headers.insert(1, 'Store')
  
  return (data, title, headers)