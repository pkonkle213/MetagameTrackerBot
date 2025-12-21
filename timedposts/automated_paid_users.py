from data.five6_users import GetFive6Users

# TODO: How do I get this to update every 5 minutes?
PAID_USERS: list[int] = []

def UpdatePaidUsers():
  global PAID_USERS
  PAID_USERS = [] + GetFive6Users()
