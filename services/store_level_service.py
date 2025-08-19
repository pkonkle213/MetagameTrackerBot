from data.events_reported_data import EventsAboveThreshold
import settings

def Level1StoreIds():
  percent = 50/100.0
  num_expected = 2
  list = GetStoreIds(percent, num_expected)
  print('Level 1 Store Ids: ', list)
  return list
  
def Level2StoreIds():
  percent = 80/100.0
  num_expected = 3
  list = GetStoreIds(percent, num_expected)
  print('Level 2 Store Ids: ', list)
  return list

def Level3StoreIds():
  percent = 95/100.0
  num_expected = 4
  list = GetStoreIds(percent, num_expected)
  print('Level 3 Store Ids: ', list)
  return list
  
def LevelInfStoreIds():
  percent = 100/100.0
  num_expected = 4
  list = GetStoreIds(percent, num_expected)
  print('Level Inf Store Ids: ', list)
  return list
  
def GetStoreIds(percent, num_expected):
  guild_ids = EventsAboveThreshold(percent, num_expected)
  total_list = AddExceptions(guild_ids)
  return total_list

def AddExceptions(idList):
  full_list = []
  full_list.append(settings.TESTGUILDID)
  full_list.append(settings.FIVE6STOREID)
  for i in idList:
    if i[0] not in full_list:
      full_list.append(i[0])
  return full_list

#TODO: See note to self about store levels
LEVEL1STORES = Level1StoreIds()
LEVEL2STORES = Level2StoreIds() #+ LEVEL1STORES
LEVEL3STORES = Level3StoreIds() #+ LEVEL2STORES
LEVELINFSTORES = LevelInfStoreIds() #+ LEVEL3STORES
