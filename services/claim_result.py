from checks import isSubmitter
from custom_errors import KnownError
from data.claim_data import GetEventAndPlayerName
from services.date_functions import ConvertToDate, GetToday, DateDifference
from select_menu_bones import SelectMenu
from services.ban_word import CanSubmitArchetypes, ContainsBadWord
from discord import Interaction
from data.archetype_data import AddArchetype
from data.event_data import GetEventMeta
from services.name_services import ConvertName
from data.claim_result_data import GetEventReportedPercentage, UpdateEvent
from tuple_conversions import ConvertToEvent, Event
from interaction_data import GetInteractionData

async def ClaimResult(interaction:Interaction, player_name:str, archetype:str, date:str):
  date_used = ConvertToDate(date)
  date_today = GetToday()
  if not isSubmitter and DateDifference(date_today, date_used) > 14:
    raise KnownError('You can only claim archetypes for events within the last 14 days. Please contact your store owner to have them submit the archetype.')

  game, format, store, userId = GetInteractionData(interaction,
                                                   game=True,
                                                   format=True,
                                                   store=True)
  archetype = archetype.upper()
  if ContainsBadWord(interaction, archetype):
    raise KnownError('Archetype contains a banned word')
  if not CanSubmitArchetypes(store.DiscordId, userId):
    raise KnownError('You have submitted too many bad archetypes. Please contact your store owner to have them submit the archetype.')

  if game.Name.upper() == 'LORCANA':
    inks = await LorcanaInkMenu(interaction)
    archetype = f'{inks} - {archetype}'
  
  player_name = ConvertName(player_name)
  (event_id,
   discord_id,
   event_date,
   game_id,
   format_id,
   last_update,
   player_name) = GetEventAndPlayerName(store.DiscordId, date, game, format, player_name)
  
  if event_id is None:
    raise KnownError('Event not found. Please check the date provided.')
  if player_name is None:
    raise KnownError('Player not found. Please check the name provided.')
  event = Event(event_id,
                discord_id,
                event_date, 
                game_id,   
                format_id,  
                last_update)

  updater_name = interaction.user.display_name.upper()
  archetype_added = AddArchetype(event_id,
                        player_name,
                        archetype,
                        userId,
                        updater_name)
  return archetype_added, event

def CheckEventPercentage(event):
  percent_reported = GetEventReportedPercentage(event.ID)
  if percent_reported is None:
    raise Exception('Unable to find event by ID: ' + event.ID)

  if percent_reported >= (event.LastUpdate + 1) / 4:
    check = UpdateEvent(event.ID)
    if check is None:
      raise Exception('Unable to update event: ' + event.ID)
    str_date = event.EventDate.strftime('%B %d')
    if event.LastUpdate + 1 < 4:
      followup = (f'Congratulations! The {str_date} event is now {percent_reported:.0%} reported!', False)
    else:
      #TODO: If the event is complete, I would like to update my data guild automatically with the metagame and attendance data
      followup = (f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!', True)
    return followup
  return None

def OneEvent(event):
  event_meta = GetEventMeta(event.ID)
  title = f"{event.EventDate.strftime('%B %d')} Meta"
  headers = ['Archetype', 'Wins']
  data = event_meta
  return title, headers, data

async def LorcanaInkMenu(interaction):
  ink_colors = [(1, 'Amber'),
                (2, 'Amethyst'),
                (3, 'Emerald'),
                (4, 'Ruby'),
                (5, 'Saphhire'),
                (6, 'Steel')]
  message = 'Please select your ink colors'
  placeholder = 'Choose your ink colors'
  inks = await SelectMenu(interaction,
                          message,
                          placeholder,
                          ink_colors,
                          2)
  inks = sorted(inks)
  if len(inks) == 2:
    return f'{inks[0][1].title()}/{inks[1][1].title()}'
  if len(inks) == 1:
    return f'{inks[0][1].title()}'