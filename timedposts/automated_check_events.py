from data.archetype_data import GetUnknownArchetypes
from data.automated_events_data import ThreeDayOldEventsWithUnknown
from discord_messages import MessageChannel
from services.date_functions import GetDaysAgo, GetToday
from output_builder import BuildTableOutput
from discord_messages import MessageUser
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
      archetypes = GetUnknownArchetypes(channel.DiscordID,
                                        channel.GameID,
                                        channel.FormatID,
                                        start_date,
                                        end_date)
      if not archetypes or len(archetypes) == 0:
        print(f'No unknown archetypes found for {channel.DiscordID}, {channel.GameID}, {channel.FormatID}') #raise KnownError('No unknown archetypes found')
  
      output = BuildTableOutput('We need your help with these archetypes!', ['Date', 'Player Name'], archetypes, None)
      output = output[:-3] + '\nTo submit yours, type and enter: /submit archetype```'
      
      #Message each channel with the unknown archetypes
      await MessageChannel(bot, output, channel.DiscordID, channel.ChannelID)
  except Exception as ex:
    await MessageUser(bot, f'Error getting events with unknown archetypes: {ex}\nChannel:{channels}', settings.PHILID)
  