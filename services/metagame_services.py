from custom_errors import KnownError
from discord import Interaction
from data.metagame_data import GetMetagame
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange

def GetMyMetagame(interaction:Interaction,
  start_date:str,
  end_date:str):
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game or not objects.format:
    raise KnownError('No store, game, or format found.')
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
  title_name = objects.format.format_name.title() if format else game.game_name.title()
  data = GetMetagame(objects.store, objects.game, objects.format, date_start, date_end)
  title = f'{title_name} metagame from {date_start} to {date_end}'
  headers = ['Deck Archetype', 'Meta %', 'Win %']
  return data, title, headers