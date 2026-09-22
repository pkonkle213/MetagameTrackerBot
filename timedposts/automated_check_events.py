from data.event_data import GetEvent
from services.one_event_details import OneEventDetails
from discord.ext import commands
from data.event_data import GetEventDetails
from tuple_conversions import Game, Format, Store
from data.interaction_data import GetObjectsFromInteraction
from data.archetype_data import GetUnknownArchetypes
from data.automated_events_data import ThreeDayOldEvents
from data.event_data import CompleteEvent
from discord_messages import MessageChannel
from services.date_functions import GetDaysAgo, GetToday
from output_builder import BuildTableOutput
from discord_messages import MessageUser
from custom_errors import KnownError
from settings import PHILID


async def EventCheck(bot: commands.Bot) -> None:
    # Find events exactly 3 days old
    events = ThreeDayOldEvents()

    # Loop through channels, see what archetypes are missing, and send the appropriate message to the appropriate channel
    for event in events:
        try:
            # Mark event as complete
            CompleteEvent(event.event_id)

            # Get all unknown archetypes
            end_date = GetToday()
            start_date = GetDaysAgo(end_date, 3)

            needed_archetypes = GetUnknownArchetypes(
                event.discord_id, event.game_id, event.format_id, start_date, end_date
            )
            if len(needed_archetypes) > 0:
                output = BuildTableOutput(
                    "We need your help with these archetypes!",
                    ["Date", "Event Name", "Player Name"],
                    needed_archetypes,
                )
                output = (
                    output[:1940]
                    + "\nTo submit an archetype, use the command `/submit archetype`"
                )
                # Message each channel with the unknown archetypes
                await MessageChannel(bot, output, event.discord_id, event.channel_id)
            elif not event.is_complete:
                real_event = GetEvent(event.event_id)
                table = OneEventDetails(real_event)
                output = BuildTableOutput(table.title, table.headers, table.data)
                # Message the newly completed event's details
                await MessageChannel(bot, output, event.discord_id, event.channel_id)
        except Exception as ex:
            await MessageUser(
                bot,
                f"Error getting events with unknown archetypes: {ex}\nChannel:{events}",
                PHILID,
            )
