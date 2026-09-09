from custom_errors import KnownError
from data.data_hubs_data import GetAllHubs
from discord_messages import MessageChannel, MessageUser
from tuple_conversions import Event, Store
from discord.ext import commands
import settings

async def MessageHubs(
  bot: commands.Bot,
  store: Store,
  event: Event,
  message:str = ''
) -> None:
  """Sends a message to the hubs that a new event has been added"""
  print('Messaging hubs!')
  try:
    hubs = GetAllHubs(event)
    name = store.store_name if store.store_name else store.discord_name
    for hub in hubs:
      try:
        await MessageChannel(bot, message, hub.discord_id, hub.channel_id)
      except Exception as e:
        await MessageChannel(bot, str(e), settings.BOTGUILDID, settings.ERRORCHANNELID)
        await MessageUser(bot, f"Error messaging hub {hub.discord_id}: {e}", settings.PHILID)
  except KnownError as e:
    return