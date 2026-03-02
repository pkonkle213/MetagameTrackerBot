from data.five6_users import GetFive6Users
from settings import PHILID

PAID_USERS: list[int] = [PHILID] + GetFive6Users()

def UpdatePaidUsers():
  global PAID_USERS
  PAID_USERS = [PHILID] + GetFive6Users()
