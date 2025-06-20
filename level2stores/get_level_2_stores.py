from level2stores.database_connection import GetStoresByPaymentLevel
import discord

def GetLevel2Stores():
  storeIds = GetStoresByPaymentLevel()
  stores = []
  for storeId in storeIds:
    store = discord.Object(id=storeId[0])
    stores.append(store)
  return stores
