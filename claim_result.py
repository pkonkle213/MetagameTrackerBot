from checks import isSubmitter
from custom_errors import DateRangeError, EventNotFoundError, BadWordError
from date_functions import ConvertToDate, GetToday, DateDifference
from flag_bad_word import CanSubmitArchetypes, ContainsBadWord
from discord import Interaction
from database_connection import AddArchetype, GetEventObj, GetPercentage, UpdateEvent, GetEventMeta
from tuple_conversions import ConvertToEvent
from interaction_data import GetInteractionData

def ClaimResult(interaction:Interaction, player_name:str, archetype:str, date:str):
  date_used = '' if date == '' else ConvertToDate(date)
  date_today = GetToday()
  if date_used != '' and not isSubmitter:
    if DateDifference(date_today, date_used) > 14:
      raise DateRangeError('You can only claim archetypes for events within the last 14 days. Please contact your store owner to have them submit the archetype.')
  else:
    date_used = None

  game, format, store, userId = GetInteractionData(interaction, game=True, format=True, store=True)
  archetype = archetype.encode('ascii', 'ignore').decode('ascii')
  if ContainsBadWord(interaction, archetype):
    raise BadWordError('Archetype contains a banned word')
  if not CanSubmitArchetypes(store.DiscordId, userId):
    raise BadWordError('You have submitted too many bad archetypes. Please contact your store owner to have them submit the archetype.')
  
  updater_name = interaction.user.display_name.upper()
  archetype = archetype.upper()
  player_name = player_name.upper()
  event = GetAndConvertEvent(store.DiscordId,
                   date_used,
                   game,
                   format,
                   player_name)
  print('Event found:', event)
  if event is None:
    raise EventNotFoundError('Event not found. Please ensure all parameters are correct')
  archetype_added = AddArchetype(event.ID,
                        player_name,
                        archetype,
                        date_today,
                        userId,
                        updater_name)
  return archetype_added, event

def CheckEventPercentage(event):
  percent_reported = GetPercentage(event.ID)
  print('Percent reported:', percent_reported)
  if percent_reported is None:
    raise Exception('Unable to find event by ID: ' + event.ID)

  print('Event last update:',event.LastUpdate)
  print('Comparison:', (event.LastUpdate + 1) / 4)
  print('Test:', percent_reported >= (event.LastUpdate + 1) / 4)
  if percent_reported >= (event.LastUpdate + 1) / 4:
    check = UpdateEvent(event.ID)
    if check is None:
      raise Exception('Unable to update event: ' + event.ID)
    str_date = event.EventDate.strftime('%B %d')
    if event.LastUpdate + 1 < 4:
      followup = (f'Congratulations! The {str_date} event is now {percent_reported:.0%} reported!', False)
    else:
      followup = (f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!', True)
    return followup
  return None

def OneEvent(event):
  event_meta = GetEventMeta(event.ID)
  title = f"{event.EventDate.strftime('%B %d')} Meta"
  headers = ['Archetype', 'Wins']
  data = event_meta
  return title, headers, data

def GetAndConvertEvent(guild_id, event_date, game, format, player_name):
  event_obj = GetEventObj(guild_id, event_date, game, format, player_name=player_name)
  if event_obj is None:
    return None
  return ConvertToEvent(event_obj)