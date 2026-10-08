from data.sync_check_data import GetFive6Users, GetStores, GetHubs
from settings import PHILID

PAID_USERS: list[int] = []
PAID_STORES: list[int] = []
PAID_HUBS: list[int] = []
STORES: list[int] = []
HUBS: list[int] = []


async def InitializePaidData() -> None:
    """Load paid-user, store, and hub caches during asynchronous bot startup."""
    global PAID_USERS, PAID_STORES, PAID_HUBS, STORES, HUBS

    PAID_USERS = [PHILID] + await GetFive6Users()
    PAID_STORES = await GetStores(paid=True)
    PAID_HUBS = await GetHubs(paid=True)
    STORES = await GetStores()
    HUBS = await GetHubs()


async def UpdateStores() -> bool:
    global STORES
    STORES = await GetStores()
    return True


async def UpdateHubs() -> None:
    global HUBS
    HUBS = await GetHubs()


async def UpdatePaidUsers() -> None:
    global PAID_USERS
    PAID_USERS = [PHILID] + await GetFive6Users()  # + GetUsers(paid=True)


async def UpdatePaidStores() -> None:
    global PAID_STORES
    PAID_STORES = await GetStores(paid=True)


async def UpdatePaidHubs() -> None:
    global PAID_HUBS
    PAID_HUBS = await GetHubs(paid=True)
