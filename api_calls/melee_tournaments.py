import settings
import requests

#TODO: This needs to be generalized for future state when multiple stores have IDs and Secrets that I need to grab from a database
def GetMeleeTournamentData(tournament_id) -> list:
  username = settings.MELEE_CLIENTID
  password = settings.MELEE_CLIENTSECRET
  page_size = 250
  has_more = True
  data = []
  page = 1

  while has_more:
    api_url = f"https://melee.gg/api/match/list/{tournament_id}?variables.page={page}&variables.pageSize={page_size}"
    response = requests.get(api_url, auth=(username, password))

    if response.status_code == 200:
      response_obj = response.json()
      data += response_obj['Content']
      has_more = response_obj['HasMore']
      page += 1
    else:
      raise Exception("Unable to get data from Melee.gg. Please try again.")
    
  return data