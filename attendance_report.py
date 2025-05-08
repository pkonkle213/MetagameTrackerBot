from discord import Interaction
from date_functions import GetToday, GetStartDate
from interaction_data import GetInteractionData
from database_connection import GetAttendance

#TODO: Make this more flexible to allow for multiple stores (DATAGUILD)
def GetStoreAttendance(interaction:Interaction):
  game, format, store, userId = GetInteractionData(interaction,
                                                   game=True,
                                                   store=True)

  date_end = GetToday()
  date_start = GetStartDate(date_end)

  data = GetAttendance(store.DiscordId,
                       game,
                       format,
                       date_start,
                       date_end)
  subject = format.FormatName.title() if game.HasFormats and format is not None else game.Name.title()
  title = f'{subject} attendance from {date_start} to {date_end}'
  headers = ['Date', 'Players']
  return (data, title, headers)