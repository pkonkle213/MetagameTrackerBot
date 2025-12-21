from data.five6_users import GetFive6Users

PAID_USERS: list[int] = [] + GetFive6Users()

def UpdatePaidUsers():
  global PAID_USERS
  PAID_USERS = [] + GetFive6Users()
