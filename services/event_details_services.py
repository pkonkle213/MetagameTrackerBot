from data.event_details_data import GetAllEventsStats

def GetEventStats(interaction, discord_id):
  data = GetAllEventsStats(discord_id)
  title = 'Unique Submitters'
  headers = ['Event Date', 'Game', 'Format','Attended', 'Users','Users Percent', 'Archetypes', 'Archetypes Percent']
  if not discord_id:
    headers.insert(1, 'Store')
  return data, title, headers
