import requests

def GetEventData(id, token):
  headers = {"X-API-Key": f"Bearer {token}"}
  url = f'https://api.spicerack.gg/api/v1/magic-events/{id}'
  response = requests.get(url, headers=headers)
  if response.status_code >= 200 and response.status_code < 300:
    data = response.json()  # If the response is in JSON format
    print(data)
  else:
    print(f"Error: {response.status_code}")