from checks import isSubmitter
from custom_errors import KnownError
from data.claim_data import GetEventAndPlayerName
from services.date_functions import ConvertToDate, GetToday, DateDifference
from select_menu_bones import SelectMenu
from services.ban_word_services import CanSubmitArchetypes, ContainsBadWord
from discord import Interaction
from data.archetype_data import AddArchetype
from data.event_data import EventIsPosted, GetEventMeta
from services.input_services import ConvertInput
from data.claim_result_data import GetEventReportedPercentage, UpdateEvent
from tuple_conversions import Event
from interaction_objects import GetObjectsFromInteraction
from output_builder import BuildTableOutput

async def AddTheArchetype(bot, interaction, player_name, date, archetype=''):
  archetype_submitted, event = await ClaimResult(interaction,
                                                 player_name,
                                                 archetype,
                                                 date)
  if archetype_submitted is None:
    raise KnownError('Unable to submit the archetype. Please try again later.')
  else:
    message = BuildMessage(interaction, date, archetype_submitted)
    feed_output = message
    private_output = f"Thank you for submitting the archetype for {event.EventDate.strftime('%B %d')}'s event!"
    public_output, event_full = CheckEventPercentage(event)
    return private_output, feed_output, public_output, event_full

def BuildMessage(interaction, date, archetype_submitted=None, error_message=None, player_name='', archetype=''):
  message_parts = []
  message_parts.append(f'Submitter: {interaction.user.display_name}')
  message_parts.append(f'Submitter id: {interaction.user.id}')
  if not archetype_submitted:
    message_parts.append(f'Ran into an error: {error_message}')
  message_parts.append(f'Archetype submitted: {archetype_submitted.Archetype if archetype_submitted else archetype}')
  message_parts.append(f'For player name: {player_name if not archetype_submitted else archetype_submitted.PlayerName}')
  message_parts.append(f'For date: {date}')
  message_parts.append(f'For channel name: {interaction.channel.name}')
  return '\n'.join(message_parts)  

async def ClaimResult(interaction:Interaction,
                      player_name:str,
                      archetype:str,
                      date:str):
  date_used = ConvertToDate(date)
  if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter') and DateDifference(GetToday(), date_used) > 14:
    raise KnownError('You can only claim archetypes for events within the last 14 days. Please contact your store owner to have them submit the archetype.')

  game, format, store, userId = GetObjectsFromInteraction(interaction,
                                                   game=True,
                                                   format=True,
                                                   store=True)
  
  if ContainsBadWord(store.DiscordId, archetype):
    raise KnownError('Archetype contains a banned word')
  if not CanSubmitArchetypes(store.DiscordId, userId):
    raise KnownError('You have submitted too many bad archetypes. Please contact your store owner to have them submit the archetype.')

  player_name = ConvertInput(player_name)

  (event, player_name) = GetEventAndPlayerName(store.DiscordId, date_used, game, format, player_name)
  
  if event is None:
    raise KnownError('Event not found. Please check the date provided. If date is correct, the event has yet to be submitted. Please alert your store owner.')
  if player_name is None:
    raise KnownError('Player not found. Please check the name provided.')
  
  if game.Name.upper() == 'LORCANA':
    inks = await LorcanaInkMenu(interaction)
    if format.IsLimited:
      archetype = f'{inks}'
    else:
      archetype = f'{inks} - {archetype}'
  
  if game.Name.upper() == 'MAGIC' and format.IsLimited:
    archetype = await MagicLimited(interaction)

  updater_name = interaction.user.display_name
  archetype_added = AddArchetype(event.ID,
                                 player_name,
                                 archetype,
                                 userId,
                                 updater_name)
  if archetype_added is None:
    raise KnownError('Unable to submit the archetype. Please try again later.')
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
      followup = f'Congratulations! The {str_date} event is now {percent_reported:.0%} reported!'
      final = None
    else:
      followup = f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!'
      title, headers, data = OneEvent(event)
      final = BuildTableOutput(title, headers, data)
      EventIsPosted(event.ID)
    return followup, final
  return None, None

def OneEvent(event):
  event_meta = GetEventMeta(event.ID)
  data = event_meta
  title = f"{event.EventDate.strftime('%B %d')} Meta ({len(data)} attended)"
  headers = ['Archetype', 'Wins', 'Losses', 'Draws']
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
  color_selections = [(1,'White','W'),
                      (2,'Blue','U'),
                      (3,'Black','B'),
                      (4,'Red','R'),
                      (5,'Green','G')]
  colors = ""
  drafted_colors = await SelectMenu(interaction, 'Please select the main colors of your deck (> 3 cards)', 'Main Colors', color_selections, 5)
  print('Drafted Colors:', drafted_colors)
  for color in drafted_colors:
    colors += color[2]
  print('Colors:', colors)
  splashed_colors = await SelectMenu(interaction, 'Please select the colors you splashed (<= 3 cards)', 'Colors Splashed', [(0,'None','N')] + color_selections, 5)
  print('Splashed Colors:', splashed_colors)
  for color in splashed_colors:
    if color[0] == 0:
      return colors
    if color[2] in colors:
      raise KnownError('You cannot splash a color you drafted. Please try again.')
    colors += color[2].lower()
  print('Colors:', colors)
  if len(colors) > 5:
    raise KnownError('Too many colors selected, please try again.')
  return colors