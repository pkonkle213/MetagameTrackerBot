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
from tuple_conversions import Event
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
  
  if game.Name.upper() == 'MAGIC' and (format.Name.upper() == 'DRAFT' or format.Name.upper() == 'SEALED'):
    archetype = await MagicLimited(interaction)

  #Overwriting the player_name with the name in the database to confirm if player_name is in the database. Maybe I rename the variables to provided_player_name and confirmed_player_name?
  player_name = ConvertName(player_name)
  (event_id,
   discord_id,
   event_date,
   game_id,
   format_id,
   last_update,
   player_name) = GetEventAndPlayerName(store.DiscordId, date_used, game, format, player_name)
  
  if event_id is None:
    raise KnownError('Event not found. Please check the date provided. If date is correct, the event has yet to be submitted. Please alert your store owner.')
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
      followup = (f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!', True)
    return followup
  return None

def OneEvent(event):
  event_meta = GetEventMeta(event.ID)
  title = f"{event.EventDate.strftime('%B %d')} Meta"
  headers = ['Archetype', 'Wins', 'Losses', 'Draws']
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

async def MagicLimited(interaction):
  print('Magic Limited')
  color_selections = [(1,'White','W'),
                      (2,'Blue','U'),
                      (3,'Black','B'),
                      (4,'Red','R'),
                      (5,'Green','G')]
  colors = ""
  drafted_colors = await SelectMenu(interaction, 'Please select the main colors of your deck (> 3 cards)', 'Main Colors', color_selections, 5)
  for color in drafted_colors:
    colors += color[2].upper()
  splashed_colors = await SelectMenu(interaction, 'Please select the colors you splashed (<= 3 cards)', 'Colors Splashed', color_selections, 5)
  for color in splashed_colors:
    colors += color[2].lower()
  if len(colors) > 5:
    raise KnownError('Too many colors selected, please try again.')
  return colors