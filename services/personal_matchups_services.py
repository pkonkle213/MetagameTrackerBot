from data.personal_matchup_data import GetPersonalMatchups
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange
from services.command_error_service import KnownError

def PersonalMatchups(interaction, start_date, end_date):
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game or not objects.format:
    raise KnownError('No Store, Game, or Format Found')
  user_id = interaction.user.id
  start_date, end_date = BuildDateRange(start_date, end_date, objects.format)
  data = GetPersonalMatchups(objects.store.discord_id, objects.game, objects.format, start_date,
    end_date, user_id)
  title = f'Personal Matchup Results between {start_date.strftime("%m/%d/%Y")} and {end_date.strftime("%m/%d/%Y")}'
  headers = [
    'Opponent Archetype',
    'Wins',
    'Losses',
    'Draws',
    'Matches',
    'Win %'
  ]
  return data, title, headers
