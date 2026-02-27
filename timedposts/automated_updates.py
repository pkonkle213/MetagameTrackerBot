import settings
from output_builder import BuildTableOutput
from data.automated_updates_data import GetDataChannels
from interaction_objects import GetStore, GetGame, GetFormat
from services.date_functions import BuildDateRange
from data.metagame_data import GetMetagame

async def UpdateDataGuild(bot):
  target_channels = GetDataChannels(settings.DATAGUILDID)
  store = GetStore(settings.DATAGUILDID)
  for channel in target_channels:
    game = GetGame(channel[1], True)
    format = GetFormat(game, channel[0], True)
    if not store or not game or not format:
      continue
    channel = bot.get_channel(channel[0])
    date_start, date_end = BuildDateRange('', '', format)
    title_name = format.FormatName.title() if format else game.GameName.title()
    data = GetMetagame(store, game, format, start_date=date_start, end_date=date_end)
    if data is not None and len(data) > 0:
      title = f'{title_name} metagame from {date_start} to {date_end}'
      headers = ['Deck Archetype', 'Meta %', 'Win %']
      output = BuildTableOutput(title, headers, data, 0 if format.IsLimited else None)
      await channel.send(output)