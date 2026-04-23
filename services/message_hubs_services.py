from data.data_hubs_data import GetAllHubs
from discord_messages import MessageChannel, MessageUser
from tuple_conversions import Event, Store
from discord.ext import commands
from services.command_error_service import Error
import settings

async def MessageHubs(
  bot: commands.Bot,
  store: Store,
  event: Event,
  message:str =''
) -> None:
  """Sends a message to the hubs that a new event has been added"""
  # Find hubs in the same region as the store and format
  hubs = GetAllHubs(event)
  name = store.store_name if store.store_name else store.discord_name
  output = f"New event submitted for {name}: {event.event_name} ({event.event_date.strftime("%B %d")}). Waiting for archetypes..." if message == '' else message
  # Message that an event with NAME and DATE was created at STORE
  for hub in hubs:
    try:
      await MessageChannel(bot, output, hub.discord_id, hub.channel_id)
    except Exception as e:
      await MessageChannel(bot, e, settings.BOTGUILDID, settings.ERRORCHANNELID)
      await MessageUser(bot, f"Error messaging hub {hub.discord_id}: {e}", settings.PHILID)
