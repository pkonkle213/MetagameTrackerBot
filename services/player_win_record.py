from discord import Interaction
from data.player_data import GetStats
from date_functions import BuildDateRange
from interaction_data import GetInteractionData

def PlayRecord(interaction:Interaction,
               start_date:str,
               end_date:str):
  game, format, store, user_id = GetInteractionData(interaction,
                                                    game=True,
                                                    store=True)
  date_start, date_end = BuildDateRange(start_date,
                                        end_date,
                                        format)
  data = GetStats(store.DiscordId,
                  game,
                  format,
                  user_id,
                  date_start,
                  date_end)
  title = f'Your Play Record from {str(date_start)} to {str(date_end)}'
  header = ['Archetype Name', 'Wins', 'Losses', 'Draws', 'Win %']
  if not format:
    header.insert(0, 'Format')
  return (data, title, header)
  