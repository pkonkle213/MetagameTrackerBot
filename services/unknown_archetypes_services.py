from discord import Interaction
from data.archetype_data import GetUnknownArchetypes
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange
from checks import isSubmitter
from services.command_error_service import KnownError

def GetAllUnknown(interaction:Interaction, start_date, end_date):
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game or not objects.format:
    raise KnownError('No Store Found')
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format, 4 if isSubmitter(interaction.guild, interaction.user, 'MTSubmitter') else 2)
  data = GetUnknownArchetypes(
    objects.store,
    objects.game,
    objects.format,
    date_start,
    date_end)
  title = f'Unknown Archetypes from {date_start.strftime("%m/%d/%Y")} to {date_end.strftime("%m/%d/%Y")}'
  headers = ['Date', 'Event Name', 'Player Name']
  return data, title, headers