from tuple_conversions import Game, Format, Store
from interaction_objects import GetStore, GetGameForStore
from data.archetype_data import GetUnknownArchetypes
from data.automated_events_data import ThreeDayOldEventsWithUnknown
from discord_messages import MessageChannel
from services.date_functions import GetDaysAgo, GetToday
from output_builder import BuildTableOutput
from discord_messages import MessageUser
from custom_errors import KnownError
import settings

async def EventCheck(bot):
  await GetEventsWithUnkown(bot)
 
async def GetEventsWithUnkown(bot):
  #Find events exactly 3 days old and need archetypes
  channels = ThreeDayOldEventsWithUnknown()
  #Loop through channels, see what archetypes are missing, and send the appropriate message to the appropriate channel
  try:
    for channel in channels:
      #Get all unknown archetypes
      end_date = GetToday()
      start_date = GetDaysAgo(end_date, 3)
      
      #Setting up dummy variables as all I need are the IDs
      store = Store(channel.discord_id, "", "", -1, "", "", False, -1, False)
      game = Game(channel.game_id, "")
      format = Format(channel.format_id, "", None, False)
      
      archetypes = GetUnknownArchetypes(store,
                                        game,
                                        format,
                                        start_date,
                                        end_date)
      if not archetypes or len(archetypes) == 0:
        print(f'No unknown archetypes found for {channel.discord_id}, {channel.game_id}, {channel.format_id}') #raise KnownError('No unknown archetypes found')
  
      output = BuildTableOutput('We need your help with these archetypes!', ['Date', 'Event Name', 'Player Name'], archetypes)
      output = output[:1940] + "\nTo submit yours, use the command `/submit archetype`"
      
      #Message each channel with the unknown archetypes
      await MessageChannel(bot, output, channel.discord_id, channel.channel_id)
  except Exception as ex:
    await MessageUser(bot, f'Error getting events with unknown archetypes: {ex}\nChannel:{channels}', settings.PHILID)
  