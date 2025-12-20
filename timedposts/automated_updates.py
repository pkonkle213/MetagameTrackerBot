from custom_errors import KnownError
from discord_messages import MessageChannel
from settings import DATAGUILDID
from output_builder import BuildTableOutput
from data.automated_updates_data import GetDataChannels
from interaction_objects import GetStore, GetGame, GetFormat
from services.date_functions import BuildDateRange
from data.metagame_data import GetMetagame
from discord.ext import commands

async def UpdateDataGuild(bot:commands.Bot):
  target_channels = GetDataChannels(DATAGUILDID)
  store = GetStore(DATAGUILDID)
  for channel_id in target_channels:
    game = GetGame(channel_id[1])
    format = GetFormat(channel_id[0])
    date_start, date_end = BuildDateRange('', '', format)
    if not game:
      raise KnownError('Not sure how my mappings failed me...')
    title_name = format.Name.title() if format else game.Name.title()
    data = GetMetagame(game, format, date_start, date_end, store)
    if len(data) > 0:
      title = f'{title_name} metagame from {date_start} to {date_end}'
      headers = ['Deck Archetype', 'Meta %', 'Win %']
      output = BuildTableOutput(title, headers, data, 0 if format.IsLimited else -1)
      await MessageChannel(bot, output, DATAGUILDID, channel_id[0])