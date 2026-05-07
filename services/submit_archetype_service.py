from typing import Tuple
import settings
from custom_errors import KnownError
from data.store_data import GetArchetypeFeed
from services.ban_word_services import CanSubmitArchetypes, ContainsBadWord
from discord import Interaction
from data.archetype_data import AddArchetype
from data.event_data import GetEventDetails
from services.input_services import ConvertInput
from data.claim_result_data import GetEventReportedPercentage, UpdateEvent
from output_builder import BuildTableOutput
from data.metagame_data import OneEventMetagame
from discord_messages import MessageChannel
from tuple_conversions import Event, Format, Store, Game, MetagameResult
from discord.ext import commands
from services.message_hubs_services import MessageHubs
from interaction_objects import GetStore
from data.archetype_data import PlayerInEvent


async def SubmitArchetype(
  bot: commands.Bot,
  interaction: Interaction,
  player_name: str,
  event: Event,
  archetype: str,
  game: Game,
  format: Format,
) -> None:
  store = GetStore(event.discord_id)
  if store is None:
    raise Exception("An event didn't have a store? Sus.")

  if not PlayerInEvent(event, player_name):
    raise KnownError("Player not found in event. Please try again.")

  # Make the call to check the archetype for banned words here
  if ContainsBadWord(event.discord_id, archetype):
    raise KnownError("Archetype contains a banned word")

  # Check if user is allowed to submit archetypes (too many banned words)
  if not CanSubmitArchetypes(event.discord_id, interaction.user.id):
    raise KnownError(
      "You have submitted too many archetypes with banned words. Please contact your store owner to have them submit the archetype."
    )

  # If not banned, add to the database
  archetype_added = AddArchetype(
    event.id,
    player_name,
    archetype,
    interaction.user.id,
    interaction.user.name,
    interaction.guild.id,
    interaction.guild.name,
  )
  if archetype_added is None:
    raise Exception("Unable to submit the archetype. Please try again later.")

  feed_output = BuildMessage(interaction, event, archetype, player_name)
  private_output = f"Thank you for submitting the archetype for {event.event_name}!"

  # If added, check if the event is fully reported
  public_output, full_event = CheckEventPercentage(event)

  # Send all output messages
  await interaction.followup.send(private_output, ephemeral=True)
  await MessageStoreFeed(bot, feed_output, interaction)
  if public_output:
    await MessageChannel(
      bot, public_output, interaction.guild_id, interaction.channel_id
    )
  if full_event:
    await MessageChannel(
      bot, full_event, interaction.guild_id, interaction.channel_id
    )
    name = store.store_name if store.store_name else store.discord_name
    output = f"```{name} - " + full_event[3:]
    await MessageHubs(bot, store, event, output)


async def MessageStoreFeed(bot, message: str, interaction: Interaction) -> None:
  """Message the store feed channel specific to the game"""
  try:
    channel_id = GetArchetypeFeed(
      interaction.guild_id, interaction.channel.category.id
    )
    await MessageChannel(bot, message, interaction.guild_id, channel_id)
  except Exception as e:
    await MessageChannel(bot, message, settings.BOTGUILDID, settings.CLAIMCHANNEL)


def AddTheArchetype(
  interaction: Interaction,
  player_name: str,
  event: Event,
  archetype: str,
  store: Store,
  game: Game,
  format: Format,
) -> Tuple[str, str, str | None, str | None]:
  userId = interaction.user.id

  updater_name = interaction.user.display_name

  archetype_added = AddArchetype(
    event[0], player_name, archetype, userId, updater_name
  )

  if archetype_added is None:
    raise KnownError("Unable to submit the archetype. Please try again later.")

  message = BuildMessage(interaction, event, archetype, player_name)
  feed_output = message
  private_output = f"Thank you for submitting the archetype for {event.event_name}!"
  public_output, event_full = CheckEventPercentage(event)
  return private_output, feed_output, public_output, event_full


def BuildMessage(
  interaction: Interaction, event: Event, archetype: str, player_name: str
) -> str:
  message_parts = []
  message_parts.append(f"Submitter Username: {interaction.user.display_name} ({interaction.user.id})")
  message_parts.append(f"Archetype submitted: {archetype}")
  message_parts.append(f"For player name: {player_name}")
  message_parts.append(f"For event name: {event.event_name}")
  message_parts.append(f"From Discord: {interaction.guild.name} ({interaction.guild.id})")
  return "\n".join(message_parts)


def CheckEventPercentage(event: Event) -> Tuple[str | None, str | None]:
  percent_reported = GetEventReportedPercentage(event.id)
  if percent_reported >= (event.last_update + 1) / 4:
    check = UpdateEvent(event.id)
    if check is None:
      raise Exception(f"Unable to update event: {event.id}")
    str_date = event.event_date.strftime("%B %-d")
    if event.last_update + 1 < 4:
      followup = f"Congratulations! {str_date}'s {event.event_name} is now {percent_reported:.0%} reported!"
      final = None
    else:
      followup = f"Congratulations! {str_date}'s {event.event_name} is now fully reported! Thank you to all who reported their archetypes!"
      title, headers, data = OneEventDetails(event)
      final = BuildTableOutput(title, headers, data)
    return followup, final
  return None, None


def OneEventMeta(event: Event) -> Tuple[str, list[str], list[MetagameResult]]:
  data = OneEventMetagame(event)
  title = f"{event.event_name}'s Metagame"
  headers = ["Archetype", "Metagame %", "Win %"]
  return title, headers, data


def OneEventDetails(
  event: Event,
) -> Tuple[str, list[str], list[Tuple[str, int, int, int]]]:
  data = GetEventDetails(event.id)
  title = f"{event.event_name} Results ({len(data)} attended)"
  headers = ["Archetype", "Wins", "Losses", "Draws"]
  return title, headers, data
