from data.events_reported_data import EventsAboveThreshold
import settings

def Level1StoreIds():
  print('Level 1 Store IDs')
  percent = 50/100.0
  num_expected = 2
  return GetStoreIds(percent, num_expected)
  
def Level2StoreIds():
  print('Level 2 Store IDs')
  percent = 85/100.0
  num_expected = 4
  return GetStoreIds(percent, num_expected)

def Level3StoreIds():
  print('Level 3 Store IDs')
  percent = 95/100.0
  num_expected = 4
  return GetStoreIds(percent, num_expected)

def LevelInfStoreIds():
  print('Level Inf Store IDs')
  percent = 100/100.0
  num_expected = 4
  return GetStoreIds(percent, num_expected)

def GetStoreIds(percent, num_expected):
  guild_ids = EventsAboveThreshold(percent, num_expected)
  total_list = AddExceptions(guild_ids)
  return total_list

def AddExceptions(idList):
  print('Id list:', idList)
  five6 = 1210746744602890310
  #test_guild = settings.TESTSTOREGUILD.ID
  full_list = []
  full_list.append(five6)
  for i in idList:
    if i[0] not in full_list:
      full_list.append(i[0])
  print('Full List:', full_list)
  return full_list