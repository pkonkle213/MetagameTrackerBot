import requests
from custom_errors import KnownError
from tuple_conversions import Store
from data.melee_api_data import GetStoreMeleeInfo

def GetMeleeTournamentData(tournament_id: str,
                           store: Store) -> list:
  storeInfo = GetStoreMeleeInfo(store)
  if not storeInfo or storeInfo.melee_client_id is None or storeInfo.melee_client_secret is None:
    raise KnownError("Store not registered for Melee.gg API. Update store settings and try again.")
  page_size = 250
  has_more = True
  data = []
  page = 1

  while has_more:
    api_url = f"https://melee.gg/api/match/list/{tournament_id}?variables.page={page}&variables.pageSize={page_size}"
    response = requests.get(api_url, auth=(storeInfo.melee_client_id, storeInfo.melee_client_secret))

    if response.status_code == 200:
      response_obj = response.json()
      data += response_obj['Content']
      has_more = response_obj['HasMore']
      page += 1
    else:
      raise Exception("Unable to get data from Melee.gg. Please try again.")

  #print('Data received:', data)
  if not data or data == []:
    raise KnownError("No data found for this tournament. Please try again.")
  return data