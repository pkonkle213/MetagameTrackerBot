
from data.event_details_data import GetAllEventsStats
from tuple_conversions import OutputToBuild

def GetEventStats(discord_id:int) -> OutputToBuild:
  data = GetAllEventsStats(discord_id)
  title = 'Event Statistics'
  headers = ['Event Date', 'Game', 'Format','Attended', 'Archetypes','Archetypes Percent', 'Distinct Users', 'Users Percent']
  if not discord_id:
    headers.insert(1, 'Store')
  return OutputToBuild(title, headers, data)
