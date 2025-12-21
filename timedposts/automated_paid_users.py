from data.five6_users import GetFive6Users

PAID_USERS: list[int] = []


def SyncPaidUsers():
  """Syncs the paid users for command permission"""

  pateron_users = []  #GetPatreonUsers()
  five6_users = GetFive6Users()

  PAID_USERS = pateron_users + five6_users
