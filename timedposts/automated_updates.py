from discord import CategoryChannel, ForumChannel
from discord.abc import PrivateChannel
from discord.ext import commands
from custom_errors import KnownError
import settings
from output_builder import BuildTableOutput
from data.automated_updates_data import GetDataChannels
from interaction_objects import GetHub, GetGame, GetFormat
from services.date_functions import BuildDateRange
from services.metagame_services import GetWholeMetagame

async def UpdateDataGuild(bot:commands.Bot):
  target_channels = GetDataChannels(settings.DATAGUILDID)
  store = GetHub(settings.DATAGUILDID)
  for data_channel in target_channels:
    game = GetGame(data_channel.category_id, True)
    format = GetFormat(game, data_channel.channel_id, True)
    if not store or not game or not format:
      continue
    channel = bot.get_channel(data_channel.channel_id)
    if not channel or isinstance(channel, ForumChannel) or isinstance(channel, CategoryChannel)or isinstance(channel, PrivateChannel):
      raise KnownError('Cannot send a message to this channel')
    date_start, date_end = BuildDateRange('', '', format)
    title_name = format.format_name.title() if format else game.game_name.title()
    data = GetWholeMetagame(
      game,
      format,
      date_start,
      date_end,
      "COALESCE(ua.archetype_played, 'Unknown') AS archetype_played,"
    )
    if len(data) > 0:
      title = f'{title_name} metagame from {date_start} to {date_end}'
      headers = ['Deck Archetype', 'Meta %', 'Win %']
      output = BuildTableOutput(title, headers, data)
      await channel.send(output)