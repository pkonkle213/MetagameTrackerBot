from store_event_reported.database_report import GetStoreReportedPercentage
from tuple_conversions import Store, Game, Format
from interaction_data import GetInteractionData

def GetMyEventsReported(interaction):
  game, format, store, user_id = GetInteractionData(interaction,
                                                    game=True,
                                                    store=True)
  data = GetStoreReportedPercentage(store.DiscordId,
                                    game,
                                    format)
  title = f'{store.StoreName.title()} Events Reported Percentage'
  headers = ['Event Date',
             'Percent Reported']
  if not format:
    headers.insert(1,'Format')
  return data, title, headers