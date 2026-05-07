import discord
from data.submitted_archetypes_data import GetSubmittedArchetypes
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import ConvertToDate
from services.input_services import ConvertInput
from tuple_conversions import OutputToBuild

def SubmittedArchetypesReport(interaction: discord.Interaction, player_name:str, event_date:str) -> OutputToBuild:
  date_used = ConvertToDate(event_date) if event_date != '' else None
  objects= GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game:
    raise Exception('No store, game, or format found')
  player_name = ConvertInput(player_name)
  data = GetSubmittedArchetypes(objects.game, objects.format, objects.store, player_name, date_used)
  headers = ['Event Date',
             'Player Name',
             'Archetype Played',
             'Submitted By',
             'Submitted By ID']
  if format is None:
    headers.insert(1, 'Format')
  title = 'Archetypes Submitted'
  if date_used is not None:
    title += f' for {date_used.strftime("%B %d")}'
  return OutputToBuild(title, headers, data)
