from data.sync_check_data import GetFive6Users, GetStores, GetHubs
from settings import PHILID

PAID_USERS: list[int]
STORES: list[int]
HUBS: list[int]

def UpdatePaidUsers() -> None:
  global PAID_USERS
  PAID_USERS = [PHILID] + GetFive6Users() #+ GetPaidUsers()

def UpdateStores() -> None:
  global STORES
  STORES = GetStores()

def UpdateHubs() -> None:
   global HUBS
   HUBS = GetHubs()