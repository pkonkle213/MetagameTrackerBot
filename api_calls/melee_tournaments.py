import requests
from custom_errors import KnownError
from tuple_conversions import Store
from data.melee_api_data import GetStoreMeleeInfo

def GetMeleeTournamentData(tournament_id:str,
                           store: Store) -> list:
  storeInfo = GetStoreMeleeInfo(store)
  if storeInfo.ClientId is None or storeInfo.ClientSecret is None:
    raise KnownError("Store not registered for Melee.gg API. Update store settings and try again.")
  page_size = 250
  has_more = True
  data = []
  page = 1

  while has_more:
    api_url = f"https://melee.gg/api/match/list/{tournament_id}?variables.page={page}&variables.pageSize={page_size}"
    response = requests.get(api_url, auth=(storeInfo.ClientId, storeInfo.ClientSecret))

    if response.status_code == 200:
      response_obj = response.json()
      data += response_obj['Content']
      has_more = response_obj['HasMore']
      page += 1
    else:
      raise Exception("Unable to get data from Melee.gg. Please try again.")
    
  return data