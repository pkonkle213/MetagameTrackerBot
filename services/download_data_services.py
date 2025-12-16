from discord import File
from io import BytesIO
from services.date_functions import BuildDateRange
from data.download_data import GetStoreStandingData, GetStorePairingData, GetPlayerPairingData, GetPlayerStandingData
from interaction_objects import GetObjectsFromInteraction

def GetStoreData(interaction, start_date, end_date):
  interactionData = GetObjectsFromInteraction(interaction, store=True)
  store = interactionData.Store
  game = interactionData.Game
  format = interactionData.Format
  
  date_start, date_end = BuildDateRange(start_date, end_date, format)

  message = f'Here is the data for {store.StoreName.title()} between {start_date} and {end_date}:'
  files = []
  
  participant_data = GetStoreStandingData(store, game, format, date_start, date_end)
  if len(participant_data) != 0:
    header = 'GAME,FORMAT,DATE,PLAYER_NAME,ARCHETYPE_PLAYED,WINS,LOSSES,DRAWS'
    files.append(ConvertRowsToFile(participant_data, 'MyStoreParticipantData', header))
    message += ' Participant data is attached.'

  round_data = GetStorePairingData(store, game, format, date_start, date_end)
  if len(round_data) != 0:
    header = 'GAME,FORMAT,DATE,ROUND,PLAYER_NAME,ARCHETYPE_PLAYED,OPPONENT_NAME,OPPONENT_ARCHETYPE,RESULT'
    files.append(ConvertRowsToFile(round_data, 'MyStoreRoundByRoundData', header))
    message += ' Round by round data is attached.'
    
  return message, files

def GetPlayerData(interaction, start_date, end_date):
  game, format, store, user_id = GetObjectsFromInteraction(interaction, store=True, game=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  
  message = f'Here is your data from {store.StoreName.title()} between {start_date} and {end_date}:'
  files = []

  participant_data = GetPlayerStandingData(store, game, format, date_start, date_end, user_id)
  if len(participant_data) != 0:
    header = 'GAME,FORMAT,DATE,ARCHETYPE_PLAYED,WINS,LOSSES,DRAWS'
    files.append(ConvertRowsToFile(participant_data, 'MyEventResultsData', header))

  round_data = GetPlayerPairingData(store, game, format, date_start, date_end, user_id)
  if len(round_data) != 0:
    header = 'GAME,FORMAT,DATE,ROUND,ARCHETYPE_PLAYED,OPPONENT_ARCHETYPE,RESULT'
    files.append(ConvertRowsToFile(round_data, 'MyRoundByRoundData', header))
    
  return message, files

def ConvertRowsToFile(data, filename, header):
  data_list = []
  data_list.append(header + '\n')
  for row in data:
    max = len(row)
    row_string = ''
    for i in range(max):
      row_string += f'{row[i]}'
      if i != max - 1:
        row_string += ','
      else:
        row_string += '\n'

    data_list.append(row_string)

  as_bytes = map(str.encode, data_list)
  content = b''.join(as_bytes)
  return File(BytesIO(content), filename=f'{filename}.csv')
  