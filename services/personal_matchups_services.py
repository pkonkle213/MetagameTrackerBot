from data.personal_matchup_data import GetPersonalMatchups
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange

def PersonalMatchups(interaction, start_date, end_date):
  game, format, store, user_id = GetObjectsFromInteraction(interaction)
  start_date, end_date = BuildDateRange(start_date, end_date, format)
  data = GetPersonalMatchups(store.DiscordId, game, format, start_date, end_date, user_id)
  title = f'Personal Matchup Results between {start_date.strftime("%m/%d/%Y")} and {end_date.strftime("%m/%d/%Y")}'
  headers = ['Opponent Archetype', 'Wins', 'Losses', 'Draws', 'Matches', 'Win %']
  return data, title, headers