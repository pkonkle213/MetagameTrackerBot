import settings
from checks import isSubmitter
from custom_errors import KnownError
from data.claim_data import GetEventAndPlayerName
from data.store_data import GetClaimFeed
from services.date_functions import ConvertToDate, GetToday, DateDifference
from services.ban_word_services import CanSubmitArchetypes, ContainsBadWord
from discord import Interaction
from input_modals.submit_archetype_modal import SubmitArchetypeModal
from data.archetype_data import AddArchetype
from data.event_data import EventIsPosted, GetEventMeta
from services.input_services import ConvertInput
from data.claim_result_data import GetEventReportedPercentage, UpdateEvent
from interaction_objects import GetObjectsFromInteraction
from output_builder import BuildTableOutput
from discord_messages import MessageChannel

#TODO: This is a lot of stuff. Needs to be broken up into smaller functions, refactored, and renamed
async def GetUserInput(interaction:Interaction) -> tuple[str, str, str]:
  data = GetObjectsFromInteraction(interaction,
                                   game=True,
                                   store=True)
  modal = SubmitArchetypeModal(data.Game, data.Format)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if data.Game.Name.upper() == 'MAGIC' and data.Format.IsLimited:
    archetype = MagicLimited(modal.submitted_main_colors,
                             modal.submitted_splash_colors)
  else:
    archetype = ConvertInput(modal.submitted_archetype)
  #TODO: Makes more sense for this to be handled in the modal?
    if data.Game.Name.upper() == 'LORCANA':
      archetype = f'{modal.submitted_inks[0]}/{modal.submitted_inks[1]} - {archetype}'
  return modal.submitted_player_name, modal.submitted_date, archetype

async def MessageStoreFeed(bot, message, interaction):
  try:
    #Message the store feed channel specific to the game
    channel_id = GetClaimFeed(interaction.guild_id,
                              interaction.channel.category.id)
    await MessageChannel(bot,
                         message,
                         interaction.guild_id,
                         channel_id)
  except Exception:
    #If none listed or found, message the bot guild
    await MessageChannel(bot,
                         message,
                         settings.BOTGUILDID,
                         settings.CLAIMCHANNEL)

async def AddTheArchetype(interaction, player_name, date, archetype):
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

  event, player_name = GetEventAndPlayerName(store.DiscordId,
                                             date_used,
                                             game,
                                             format,
                                             player_name)
  
  if event is None:
    raise KnownError('Event not found. Please check the date provided. If date is correct, the event has yet to be submitted. Please alert your store owner.')
  if player_name is None:
    raise KnownError('Player not found. Please check the name provided.')

  updater_name = interaction.user.display_name
  archetype_added = AddArchetype(event.ID,
                                 player_name,
                                 archetype,
                                 userId,
                                 updater_name)
  if archetype_added is None:
    raise Exception('Unable to submit the archetype. Please try again later.')
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

def MagicLimited(drafted_colors:list, splashed_colors:list) -> str:
  colors = ""
  for color in drafted_colors:
    colors += ConvertMagicColor(color)

  if len(splashed_colors) == 0:
    return colors
  for color in splashed_colors:
    letter = ConvertMagicColor(color)
    if letter in colors:
      raise KnownError('You cannot splash a color you drafted. Please try again.')
    colors += letter.lower()
  print('Colors:', colors)
  if len(colors) > 5:
    raise KnownError('Too many colors selected, please try again.')
  return colors

def ConvertMagicColor(color:str) -> str:
  match color:
   case 'White':
     return 'W'
   case 'Blue':
     return 'U'
   case 'Black':
     return 'B'
   case 'Red':
     return 'R'
   case 'Green':
     return 'G'
   case _:
     raise KnownError('Color not recognized. Please try again.')