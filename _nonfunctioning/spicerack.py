import tuple_conversions
import requests
import database_connection

def GetSpicerackData(discord_id, event_id):
  store_obj = database_connection.GetStoreByDiscord(discord_id = discord_id)
  if store_obj is None:
    raise Exception('Store not found')
  store = tuple_conversions.ConvertToStore(store_obj[0])
  #Check that the event_id hasn't been submitted yet
  spicerack_id = database_connection.GetSpiceId(event_id)
  if spicerack_id:
    return 'This event has already been submitted'

  #Get the event data from spicerack
  data = spicerack.GetEventData(store.DiscordId, event_id)

  event = GetEvent(discord_id, date_of_event, game, format)
  if event is None:
    event = CreateEvent(date_of_event, message.guild.id, game, format)

  output = AddResults(event_id, data, store.OwnerId, event_id)

  #import the data into the database
  #report the results
  output = 'Success??'
  return output

def GetEventData(discord_id, event_id):
  store = database_connection.GetStoreByDiscord(discord_id=discord_id)
  if store is None:
    raise Exception("Store not found")

  store = tuple_conversions.ConvertToStore(store[0])
  headers = {"X-API-Key": f"{store.SpicerackKey}"}
  url = 'https://api.spicerack.gg/api/v1/magic-events/'
  if event_id != 0:
    url += f'{event_id}/'
  response = requests.get(url, headers=headers)
  if not (response.status_code >= 200 and response.status_code < 300):
    raise Exception(f"Error finding spicerack event: {response.status_code}")
  data = response.json() 

  players = None
  event = None
  if 'id' not in data:
    complete = False
    i = 0
    while not complete:
      try:
        event = data[i]
        if event['settings']['event_lifecycle_status'] == 'EVENT_FINISHED':
          complete = True
        else:
          i += 1
      except Exception:
        raise Exception("Completed event not found")
  else:
    event = data
    
  if event is not None:
    players = ConvertEventToPlayers(event)
    return players

def ConvertEventToPlayers(event):
  players = []
  for player in event['user_statuses']:
    player_name = player['user']['best_identifier']
    wins = player['matches_won']
    losses = player['matches_lost']
    draws = player['matches_drawn']
    players.append(tuple_conversions.Participant(player_name, wins, losses, draws))

  return players