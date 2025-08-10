import settings
from output_builder import BuildTableOutput
from data.automated_updates_data import GetDataChannels
from interaction_data import GetGame, GetFormat
from services.date_functions import BuildDateRange
from data.metagame_data import GetMetagame
from interaction_data import GetStore

async def UpdateDataGuild(bot):
  target_channels = GetDataChannels(settings.DATAGUILDID)
  store = GetStore(settings.DATAGUILDID)
  for channel in target_channels:
    game = GetGame(channel[1], True)
    format = GetFormat(game, channel[0], True)
    channel = bot.get_channel(channel[0])
    date_start, date_end = BuildDateRange('', '', format)
    title_name = format.Name.title() if format else game.Name.title()
    data = GetMetagame(game, format, date_start, date_end, store)
    if data is None or len(data) == 0:
      await channel.send('No metagame data found for this format')
    else:
      title = f'{title_name} metagame from {date_start} to {date_end}'
      headers = ['Deck Archetype', 'Meta %', 'Win %', 'Combined %']
      output = BuildTableOutput(title, headers, data)
      await channel.send(output)