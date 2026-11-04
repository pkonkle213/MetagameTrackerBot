from discord import Interaction
from discord.ext import commands

import settings
from api_calls.moxfield_decklist import GetMoxfieldArchetype
from custom_errors import KnownError
from data.archetype_data import BulkAddArchetypes, PlayerInEvent
from data.claim_result_data import GetEventReportedPercentage, UpdateEvent
from data.store_data import GetArchetypeFeed, GetFormatMapByEvent
from discord_messages import MessageChannel
from output_builder import BuildTableOutput
from services.ban_word_services import CanSubmitArchetypes, ContainsBadWord
from services.message_hubs_services import MessageHubs
from services.one_event_details import OneEventDetails
from tuple_conversions import (
    Event,
    Format,
    Game,
    Hub,
    PlayerArchetype,
    Store,
)


async def Moxfield(
    link: str, event: Event, format: Format, player_name: str
) -> tuple[str, str, bool]:
    try:
        moxfield_archetype = await GetMoxfieldArchetype(
            link, event, format, player_name
        )
        return moxfield_archetype, "", True
    except KnownError:
        return (
            "",
            (" Unable to load the decklist from Moxfield. Please try again later."),
            False,
        )


async def SubmitArchetype(
    bot: commands.Bot,
    interaction: Interaction,
    player_name: str,
    event: Event,
    archetype: str,
    store: Store | None,
    hub: Hub | None,
    game: Game,
    format: Format,
    moxfield_link: str | None,
    is_submitter: bool,
) -> None:
    ValidateArchetypeContext(interaction)
    await ValidateArchetypeSubmission(interaction, event, player_name, archetype)

    moxfield_error = ""
    if moxfield_link:
        imported_archetype, moxfield_error, moxfield_success = await Moxfield(
            moxfield_link, event, format, player_name
        )
        if moxfield_success:
            archetype = imported_archetype
            await ValidateArchetypeSubmission(
                interaction, event, player_name, archetype
            )

    if not archetype:
        raise KnownError("No archetype submitted. Please try again." + moxfield_error)

    await SaveArchetypeSubmission(
        interaction, event, player_name, archetype, is_submitter
    )

    await NotifyArchetypeSubmission(
        bot,
        interaction,
        event,
        [PlayerArchetype(player_name, archetype)],
        store,
        moxfield_error,
    )


def ValidateArchetypeContext(interaction: Interaction) -> None:
    if interaction.guild is None or interaction.channel is None:
        raise KnownError("Archetypes can only be submitted in a server channel.")


async def ValidateArchetypeSubmission(
    interaction: Interaction, event: Event, player_name: str, archetype: str
) -> None:
    if not await PlayerInEvent(event, player_name):
        raise KnownError(
            f"Player name `{player_name}` not found in event. Please try again."
        )

    if await ContainsBadWord(event.discord_id, archetype):
        raise KnownError("Archetype contains a banned word")

    if not await CanSubmitArchetypes(event.discord_id, interaction.user.id):
        raise KnownError(
            "You have submitted too many archetypes with banned words. "
            "Please contact your store owner to have them submit the archetype."
        )


async def SaveArchetypeSubmission(
    interaction: Interaction,
    event: Event,
    player_name: str,
    archetype: str,
    is_submitter: bool,
) -> None:
    if not archetype:
        return
    await BulkAddArchetypes(
        event,
        [PlayerArchetype(player_name, archetype)],
        interaction.user.id,
        interaction.user.name,
        interaction.guild_id,
        interaction.guild.name if interaction.guild else "",
        is_submitter,
    )


async def NotifyArchetypeSubmission(
    bot: commands.Bot,
    interaction: Interaction,
    event: Event,
    archetypes: list[PlayerArchetype],
    store: Store | None,
    moxfield_error: str,
) -> Event:
    submission_label = "archetype" if len(archetypes) == 1 else "archetypes"
    private_output = (
        f"Thank you for submitting {submission_label} for {event.event_name}!"
        + moxfield_error
    )
    await interaction.followup.send(private_output, ephemeral=True)
    await MessageStoreFeed(bot, BuildMessage(interaction, event, archetypes), event)

    public_output, full_event, updates_counted = await CheckEventPercentage(event)
    if updates_counted:
        event = event._replace(last_update=event.last_update + updates_counted)
    format_map = await GetFormatMapByEvent(event)
    mapped_channel = format_map.channel_id

    if public_output:
        await MessageChannel(bot, public_output, event.discord_id, mapped_channel)

    # TODO: This is broken and needs fixed (broke it by updating the table builder)
    if full_event:
        await MessageChannel(bot, full_event, interaction.guild_id, mapped_channel)
        await MessageHubs(
            bot, store, event, f"```{event.event_name} - " + full_event[3:]
        )
    return event


async def MessageStoreFeed(bot: commands.Bot, message: str, event: Event) -> None:
    """Message the store feed channel specific to the game"""
    try:
        channel_id = await GetArchetypeFeed(event.discord_id, event.game_id)
        await MessageChannel(bot, message, event.discord_id, channel_id)
    except Exception as e:
        await MessageChannel(bot, message, settings.BOTGUILDID, settings.CLAIMCHANNEL)


def BuildMessage(
    interaction: Interaction, event: Event, archetypes: list[PlayerArchetype]
) -> str:
    message_parts = ["```"]
    message_parts.append(
        f"Submitter Username: {interaction.user.display_name} ({interaction.user.id})"
    )
    for archetype in archetypes:
        message_parts.append(f"Archetype submitted: {archetype.archetype_played}")
        message_parts.append(f"For player name: {archetype.player_name}")
    message_parts.append(f"For event name: {event.event_name}")
    message_parts.append(
        f"From Discord: {interaction.guild.name} ({interaction.guild.id})"
    )
    message_parts.append("```")
    return "\n".join(message_parts)


async def CheckEventPercentage(
    event: Event,
) -> tuple[str | None, str | None, int]:
    followup: str | None = None
    final: list[str] | None = None
    percent_reported = await GetEventReportedPercentage(event.id)
    target_update = min(4, int(percent_reported * 4))
    updates_counted = max(0, target_update - event.last_update)
    print("target:", target_update)
    print("counted:", updates_counted)

    if updates_counted:
        for _ in range(updates_counted):
            await UpdateEvent(event.id, target_update)

        str_date = event.event_date.strftime("%B %-d")
        if event.last_update + updates_counted < 4:
            followup = f"Congratulations! {str_date}'s {event.event_name} is now {percent_reported:.0%} reported!"
        elif event.is_complete:
            followup = f"Congratulations! {str_date}'s {event.event_name} is now fully reported! Thank you to all who reported their archetypes!"
            table = await OneEventDetails(event)
            final = BuildTableOutput(table.title, table.headers, table.data)
    final_out = final[0] if final else None
    return followup, final_out, updates_counted
