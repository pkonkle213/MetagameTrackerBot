from data.personal_matchup_data import GetPersonalMatchups
from interaction_data import GetInteractionData
from services.date_functions import BuildDateRange

def PersonalMatchups(interaction, start_date, end_date):
  game, format, store, user_id = GetInteractionData(interaction,
                                                    game=True,
                                                    format=True,
                                                    store=True)
  start_date, end_date = BuildDateRange(start_date, end_date, format)
  data = GetPersonalMatchups(store.DiscordId, game, format, start_date, end_date, user_id)
  title = f'{store.StoreName.title()} {game.Name.title()} {format.FormatName.title()} Personal Matchups'
  headers = ['Opponent Archetype', 'Wins', 'Losses', 'Draws', 'Matches', 'Win %']
  return data, title, headers