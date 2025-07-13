from discord import Interaction
from data.metagame_data import GetMetagame
from interaction_data import GetInteractionData
from services.date_functions import BuildDateRange

def GetMyMetagame(interaction:Interaction,
  start_date:str,
  end_date:str):
  game, format, store, userId = GetInteractionData(interaction, game=True, format=True, store=True)  
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  title_name = format.Name.title() if format else game.Name.title()
  data = GetMetagame(game, format, date_start, date_end, store)
  title = f'{title_name} metagame from {date_start} to {date_end}'
  headers = ['Deck Archetype', 'Meta %', 'Win %', 'Combined %']
  
  return (data, title, headers)