from data.events_reported_data import GetStoreReportedPercentage

def GetMyEventsReported(discord_id):
  data = GetStoreReportedPercentage(discord_id)
  title = 'Events Reported Percentage'
  headers = ['Event Date',
             'Store Name',
             'Game',
             'Format',
             'Reported',
             'Attended',
             'Percent']
  return data, title, headers