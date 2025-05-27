from discord import Interaction
from database_connection import GetDataRowsForMetagame
from interaction_data import GetInteractionData
from date_functions.date_functions import BuildDateRange

def GetMyMetagame(interaction:Interaction,
  start_date:str,
  end_date:str):
  game, format, store, userId = GetInteractionData(interaction, game=True, format=True, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  print('Metagame date range:', date_start, date_end)
  title_name = format.FormatName.title() if format else game.Name.title()
  data = GetDataRowsForMetagame(game, format, date_start, date_end, store)
  title = f'{title_name} metagame from {date_start} to {date_end}'
  headers = ['Deck Archetype', 'Meta %', 'Win %', 'Combined %']
  
  return (data, title, headers)