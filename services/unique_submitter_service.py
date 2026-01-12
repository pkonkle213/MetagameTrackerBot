from data.unique_submitters_data import GetUniqueSubmittersPercentage

def GetUniqueSubmitters(interaction, discord_id):
  data = GetUniqueSubmittersPercentage(discord_id)
  title = 'Unique Submitters'
  headers = ['Event Date', 'Game', 'Format', 'Reported', 'Attended', 'Percent']
  if not discord_id:
    headers.insert(1, 'Store')
  return data, title, headers
