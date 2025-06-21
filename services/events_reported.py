from data.events_reported_data import GetStoreReportedPercentage

def GetMyEventsReported(interaction, discord_id):
  data = GetStoreReportedPercentage(discord_id)
  title = 'Events Reported Percentage'
  headers = ['Event Date',
             'Store Name',
             'Format',
             'Percent Reported']
  return data, title, headers