import settings
import requests

API_URL = "https://melee.gg/api/match/list/"
PAGE_SIZE = "?variables.pageSize=250"

#TODO: There is pagination in the data received, so for larger events I would need to while-loop through until "HasMore" is false
#Which realistically means that instead of returning data, I need to build data['Content'] and test data['HasMore']
def GetMeleeTournamentData(tournament_id) -> dict:
  username = settings.MELEE_CLIENTID
  password = settings.MELEE_CLIENTSECRET
  response = requests.get(API_URL + tournament_id + PAGE_SIZE, auth=(username, password))
  content = []

  if response.status_code == 200:
    data = response.json()
    return data
  else:
    raise Exception("Unable to get data from Melee.gg. Please try again.")
    