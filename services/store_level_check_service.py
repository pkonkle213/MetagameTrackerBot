from interaction_data import GetStore
from data.check_level_data import CheckLevel, EventReportedDetails

def CheckMyStoreLevel(interaction):
  store = GetStore(interaction.guild.id, True)
  level = CheckLevel(store)
  return level

def GetLevelDetails(interaction):
  store = GetStore(interaction.guild.id, True)
  data = EventReportedDetails(store)
  title = "Your store's last 40 days of events"
  headers = ['Event Date', 'Game', 'Format', 'Reported', 'Total Attended', 'Reported %']
  return data, title, headers