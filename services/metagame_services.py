from custom_errors import KnownError
from discord import Interaction
from data.metagame_data import GetMetagame
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange

def GetMyMetagame(interaction:Interaction,
  start_date:str,
  end_date:str):
  store, game, format = GetObjectsFromInteraction(interaction)
  if not store or not game or not format:
    raise KnownError('No store, game, or format found.')
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  title_name = format.FormatName.title() if format else game.GameName.title()
  data = GetMetagame(store, game, format, start_date=date_start, end_date=date_end )
  title = f'{title_name} metagame from {date_start} to {date_end}'
  headers = ['Deck Archetype', 'Meta %', 'Win %']
  archetype_column = 0 if format and format.IsLimited else None
  return data, title, headers, archetype_column