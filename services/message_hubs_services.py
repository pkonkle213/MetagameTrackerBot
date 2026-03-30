from data.data_hubs_data import GetHubs
from discord_messages import MessageChannel, MessageUser
from tuple_conversions import Event, Store
from discord.ext import commands
from data.data_hubs_data import GetChannelFormatLocked, GetChannelGeneralHub
from services.command_error_service import Error
import settings

async def MessageHubs(bot: commands.Bot, store: Store, event: Event, message:str ='') -> None:
    """Sends a message to the hubs that a new event has been added"""
    # Find hubs in the same region as the store and format
    hubs = GetHubs(store, event)
    output = f"New event submitted for {store.store_name}: {event.event_name} ({event.event_date.strftime("%B %d")})" if message == '' else message
    # Message that an event with NAME and DATE was created at STORE
    for hub in hubs:
        try:
            if hub.hub_format_lock:
                # If the hub is a format locked hub, I need to find the channel that has the right region
                channel_id = GetChannelFormatLocked(hub, store)
                await MessageChannel(
                    bot, output, hub.discord_id, channel_id
                )
            else:
                # If the hub is a general hub, I need to find the channel that has the right format
                channel_id = GetChannelGeneralHub(hub, event)
                await MessageChannel(
                    bot, output, hub.discord_id, channel_id
                )
        except Exception as e:
            await MessageChannel(bot, e, settings.BOTGUILDID, settings.ERRORCHANNELID)
            await MessageUser(bot, f"Error messaging hub {hub.discord_name}: {e}", settings.PHILID)
