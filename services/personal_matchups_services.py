from discord import Interaction
from data.personal_matchup_data import GetPersonalMatchups
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange
from services.command_error_service import KnownError
from tuple_conversions import OutputToBuild

def PersonalMatchups(interaction:Interaction, start_date:str, end_date:str) -> OutputToBuild:
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game or not objects.format:
    raise KnownError('No Store, Game, or Format Found')
  user_id = interaction.user.id
  date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
  data = GetPersonalMatchups(
    objects.store.discord_id, 
    objects.game, 
    objects.format, 
    date_start,
    date_end, 
    user_id
  )
  title = f'Personal Matchup Results between {date_start.strftime("%m/%d/%Y")} and {date_end.strftime("%m/%d/%Y")}'
  headers = [
    'Opponent Archetype',
    'Matches',
    'Wins',
    'Losses',
    'Draws',
    'Win %'
  ]
  return OutputToBuild(title, headers, data)
