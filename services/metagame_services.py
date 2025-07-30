from discord import Interaction
from data.metagame_data import GetMetagame
from interaction_data import GetInteractionData
from services.date_functions import BuildDateRange

def GetMyMetagame(interaction:Interaction,
                  start_date:str,
                  end_date:str,
                  sort_order:int):
  game, format, store, userId = GetInteractionData(interaction, game=True, format=True, store=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  title_name = format.Name.title() if format else game.Name.title()
  data = GetMetagame(game, format, date_start, date_end, store, sort_order)
  title = f'{title_name} metagame from {date_start} to {date_end}'
  headers = ['Deck Archetype', 'Meta %', 'Win %']
  if sort_order == 4:
    headers.append('Combined %')
  
  return (data, title, headers, format.IsLimited if format else False)