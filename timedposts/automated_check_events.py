from data.archetype_data import GetUnknownArchetypes
from data.automated_events_data import ThreeDayOldEventsWithUnknown, GetCompletedUnpostedEvents
from data.event_data import EventIsPosted
from discord_messages import MessageChannel
from services.claim_result_services import OneEvent
from services.date_functions import GetDaysAgo, GetToday
from output_builder import BuildTableOutput
from discord_messages import MessageUser
import settings

#This needs to be split into two functions, that would make sense.
async def EventCheck(bot):
  try:
    await MessageUser(bot, 'Checking events for unknown archetypes...', settings.PHILID)
    await GetEventsWithUnkown(bot)
    await MessageUser(bot, 'Checking events for completed unposted events...', settings.PHILID)
    await GetCompletedEvents(bot)
    await MessageUser(bot, 'All done!', settings.PHILID)
  except Exception as error:
    await MessageUser(bot, f'Error checking events: {error}', settings.PHILID)

async def GetCompletedEvents(bot):
  #Find events exactly 3 days old and are marked as complete (aka not expecting any more input), no unknown archetypes, but has not been posted
  events = GetCompletedUnpostedEvents()

  for event in events:
    title, headers, data = OneEvent(event.ID)
    output = BuildTableOutput(title, headers, data)
    await MessageChannel(bot, output, event.DiscordID, event.ChannelID)
    EventIsPosted(event.ID)

async def GetEventsWithUnkown(bot):
  #Find events exactly 3 days old and need archetypes
  channels = ThreeDayOldEventsWithUnknown()
  #Loop through channels, see what archetypes are missing, and send the appropriate message to the appropriate channel
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

    output = BuildTableOutput('Unknown Archetypes', ['Date', 'Player Name'], archetypes, None)
    output = output[:-3] + '\nTo submit yours, type and enter: /submit archetype```'
    await MessageUser(bot, output, settings.PHILID)
    #Message each channel with the unknown archetypes
    #await MessageChannel(bot, output, channel.DiscordID, channel.ChannelID)
  
  """
  Other changes: Data input needs a dropdown for IsEventComplete
               : Claim may need to mark an event as posted
  """
  