from database_connection import SetStoreTrackingStatus
from tuple_conversions import ConvertToStore

def ApproveMyStore(discord_id):
  return SetApproval(discord_id, True)

def DisapproveMyStore(discord_id):
  return SetApproval(discord_id, False)

def SetApproval(discord_id, approval_status):
  store_obj = SetStoreTrackingStatus(approval_status, discord_id)
  if store_obj is None:
    raise Exception(f'No store found with discord id {discord_id}')
  store = ConvertToStore(store_obj)
  return store