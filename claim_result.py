import date_functions
from discord import Interaction
import database_connection
import tuple_conversions
from interaction_data import GetInteractionData

#TODO: Break this down into smaller functions to provide more specific error messages
def ClaimResult(interaction:Interaction, player_name:str, archetype:str, date:str):
  date_actual = date_functions.ConvertToDate(date)
  date_today = date_functions.GetToday()
  if date_actual is not None and date_functions.DateDifference(date_today, date_actual) > 14:
    raise Exception('You can only claim archetypes for events within the last 14 days')

  game, format, store, userId = GetInteractionData(interaction, game=True, format=True, store=True)
  updater_id = interaction.user.id
  updater_name = interaction.user.display_name.upper()
  archetype = archetype.upper()
  event = GetEvent(store.DiscordId, date_actual, game, format)
  if event is None:
    raise Exception('Event not found')
  output = database_connection.Claim(event.ID,
                 player_name,
                 archetype,
                 updater_id)
  if output is None:
    raise Exception(f'{player_name.title()} was not found in that event. The name spelling should match what was put into Companion')
  #TODO: This should double check that the information was stored
  database_connection.TrackInput(store.DiscordId,
            event.ID,
            updater_name.upper(),
            updater_id,
            archetype,
            date_functions.GetToday(),
            player_name.upper())
  
  percent_reported = database_connection.GetPercentage(event.ID)
  if percent_reported >= (event.LastUpdate + 1) / 4:
    database_connection.UpdateEvent(event.ID)
    if event.LastUpdate + 1 < 4:
      return f'Congratulations! The {date_functions.FormatDate(event.EventDate)} event is now {percent_reported:.0%} reported!'
    else:
      str_date = date_functions.FormatDate(event.EventDate)
      output = f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!\n\n'
      database_connection.UpdateEvent(event.ID)
      event_meta = database_connection.GetEventMeta(event.ID)
      title = f'{str_date} Meta'
      headers = ['Archetype', 'Wins']
      data = event_meta
      
      return title, headers, data
  return None, None, None

def GetEvent(guild_id, event_date, game, format):
  event_obj = database_connection.GetEvent(guild_id, event_date, game, format)
  if event_obj is None:
    return None
  return tuple_conversions.ConvertToEvent(event_obj)