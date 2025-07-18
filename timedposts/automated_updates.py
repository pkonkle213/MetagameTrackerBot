import settings
from output_builder import BuildTableOutput
from timedposts.automated_updates_data import GetDataChannels
from interaction_data import GetGame, GetFormat
from services.date_functions import BuildDateRange
from data.metagame_data import GetMetagame

async def UpdateDataGuild(bot):
  data_guild_id = settings.DATAGUILDID
  target_channels = GetDataChannels(data_guild_id)
  store = None #GetStore(data_guild_id, True) 
  for channel in target_channels:
    game = GetGame(channel[1], True)
    format = GetFormat(game, channel[0], True)
    channel = bot.get_channel(channel[0])
    date_start, date_end = BuildDateRange('', '', format)
    title_name = format.Name.title() if format else game.Name.title()
    data = GetMetagame(game, format, date_start, date_end, store, 4)
    if data is None or len(data) == 0:
      await channel.send('No metagame data found for this format')
    else:
      title = f'{title_name} metagame from {date_start} to {date_end}'
      headers = ['Deck Archetype', 'Meta %', 'Win %', 'Combined %']
      output = BuildTableOutput(title, headers, data)
      await channel.send(output)