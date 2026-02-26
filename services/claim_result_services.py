from datetime import datetime
from typing import Tuple
import settings
from custom_errors import KnownError
from data.store_data import GetClaimFeed
from services.ban_word_services import CanSubmitArchetypes, ContainsBadWord
from discord import Interaction
from input_modals.submit_archetype_modal import SubmitArchetypeModal
from data.archetype_data import AddArchetype
from data.event_data import GetEventMeta
from services.input_services import ConvertInput
from data.claim_result_data import GetEventReportedPercentage, UpdateEvent
from output_builder import BuildTableOutput
from discord_messages import MessageChannel
from tuple_conversions import Event, Format, Store, Game

async def GetUserInput(
  store:Store,
  game:Game,
  format:Format,
  userId:int,
  interaction:Interaction
) -> Tuple[str, Event, str]:
  modal = SubmitArchetypeModal(store, game, format, userId)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if game.GameName.upper() == 'MAGIC' and format.IsLimited:
    archetype = MagicLimited(modal.submitted_main_colors,
                             modal.submitted_splash_colors)
  else:
    archetype = ConvertInput(modal.submitted_archetype)
  #TODO: Makes more sense for this to be handled in the modal?
    if game.GameName.upper() == 'LORCANA':
      archetype = f'{modal.submitted_inks[0]}/{modal.submitted_inks[1]} - {archetype}'

  if not modal.submitted_event:
    raise KnownError('No event selected. Please try again.')
  
  return modal.submitted_player_name, modal.submitted_event, archetype

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

async def AddTheArchetype(
  interaction:Interaction,
  player_name:str,
  event:Event,
  archetype:str,
  store:Store,
  game:Game,
  format:Format
) -> Tuple[str, str, str|None, str|None]:
  player_name = ConvertInput(player_name)
  archetype_submitted = await ClaimResult(interaction,
                                          player_name,
                                          archetype,
                                          event,
                                          store,
                                          game,
                                          format)
  if archetype_submitted is None:
    raise KnownError('Unable to submit the archetype. Please try again later.')
  else:
    message = BuildMessage(interaction, event, archetype, player_name)
    feed_output = message
    private_output = f"Thank you for submitting the archetype for {event.event_name}!"
    public_output, event_full = CheckEventPercentage(event)
    return private_output, feed_output, public_output, event_full

def BuildMessage(
  interaction:Interaction,
  event:Event,
  archetype:str,
  player_name:str
) -> str:
  message_parts = []
  message_parts.append(f'Submitter: {interaction.user.display_name}')
  message_parts.append(f'Submitter id: {interaction.user.id}')
  message_parts.append(f'Archetype submitted: {archetype}')
  message_parts.append(f'For player name: {player_name}')
  message_parts.append(f'For event name: {event.event_name}')
  message_parts.append(f'For channel name: {interaction.channel.name}')
  return '\n'.join(message_parts)  

async def ClaimResult(
  interaction:Interaction,
  player_name:str,
  archetype:str,
  event:Event,
  store:Store,
  game:Game,
  format:Format
) -> int:
  #TODO: Using event_id eliminates the need for checking if the user is a submitter. Check other references to ensure this is the same in other areas

  userId = interaction.user.id
  
  if ContainsBadWord(store.DiscordId, archetype):
    raise KnownError('Archetype contains a banned word')
  if not CanSubmitArchetypes(store.DiscordId, userId):
    raise KnownError('You have submitted too many bad archetypes. Please contact your store owner to have them submit the archetype.')

  updater_name = interaction.user.display_name

  archetype_added = AddArchetype(event[0],
                                 player_name,
                                 archetype,
                                 userId,
                                 updater_name)
  if archetype_added is None:
    raise Exception('Unable to submit the archetype. Please try again later.')
  return archetype_added

def CheckEventPercentage(event:Event) -> Tuple[str | None, str | None]:
  percent_reported = GetEventReportedPercentage(event.id)
  if percent_reported is None:
    raise Exception(f'Unable to find event by ID: {event.id}')
  if percent_reported >= (event.last_update + 1) / 4:
    check = UpdateEvent(event.id)
    if check is None:
      raise Exception(f'Unable to update event: {event.id}')
    str_date = event.event_date.strftime('%B %d')
    if event.last_update + 1 < 4:
      followup = f'Congratulations! The {str_date} event is now {percent_reported:.0%} reported!'
      final = None
    else:
      followup = f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!'
      title, headers, data = OneEvent(event)
      final = BuildTableOutput(title, headers, data)
    return followup, final
  return None, None

def OneEvent(event:Event) -> Tuple[str,list[str],list[Tuple[str, int, int, int]]]:
  data = GetEventMeta(event.id)
  title = f"{event.event_name} Results ({len(data)} attended)"
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