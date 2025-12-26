import discord
from data.submitted_archetypes_data import GetSubmittedArchetypes
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import ConvertToDate
from services.input_services import ConvertInput

def SubmittedArchetypesReport(interaction: discord.Interaction, player_name, event_date):
  date_used = ConvertToDate(event_date) if event_date != '' else None

  game, format, store, user_id = GetObjectsFromInteraction(interaction)
  player_name = ConvertInput(player_name)
  data = GetSubmittedArchetypes(game, format, store, player_name, date_used)
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
  archetype_column = 2 if format and format.IsLimited else None
  return data, headers, title, archetype_column
