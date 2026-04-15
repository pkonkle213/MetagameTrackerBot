from data.sync_check_data import GetFive6Users, GetStores, GetHubs
from settings import PHILID

PAID_USERS: list[int] = GetFive6Users()
PAID_STORES: list[int] = GetStores(True)
PAID_HUBS: list[int] = GetHubs(True)
STORES: list[int] = GetStores()
HUBS: list[int] = GetHubs()

def UpdatePaidUsers() -> None:
  global PAID_USERS
  PAID_USERS = GetFive6Users() #+ GetPaidUsers()

def UpdateStores() -> None:
  global STORES
  STORES = GetStores()

def UpdateHubs() -> None:
  global HUBS
  HUBS = GetHubs()

def UpdatePaidStores() -> None:
  global PAID_STORES
  PAID_STORES = GetStores(True)

def UpdatePaidHubs() -> None:
  global PAID_HUBS
  PAID_HUBS = GetHubs(True)
