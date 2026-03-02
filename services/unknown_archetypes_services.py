from discord import Interaction
from data.archetype_data import GetUnknownArchetypes
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange
from checks import isSubmitter
from services.command_error_service import KnownError

def GetAllUnknown(interaction:Interaction, start_date, end_date):
  store, game, format  = GetObjectsFromInteraction(interaction)
  if not store:
    raise KnownError('No Store Found')
  date_start, date_end = BuildDateRange(start_date, end_date, format, 4 if isSubmitter(interaction.guild, interaction.user, 'MTSubmitter') else 2)
  data = GetUnknownArchetypes(store,
    game,
    format,
    date_start,
    date_end)
  title = f'Unknown Archetypes from {date_start.strftime("%m/%d/%Y")} to {date_end.strftime("%m/%d/%Y")}'
  headers = ['Date', 'Event Name', 'Player Name']
  return data, title, headers