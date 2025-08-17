from discord import File
from io import BytesIO
from services.date_functions import BuildDateRange
from data.download_data import GetStoreParticipantData, GetStoreRoundData, GetPlayerRoundData, GetPlayerParticipantData
from interaction_data import GetInteractionData

def GetStoreData(interaction, start_date, end_date):
  game, format, store, user_id = GetInteractionData(interaction, store=True, game=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)

  message = f'Here is the data for {store.StoreName.title()}:'
  files = []
  
  participant_data = GetStoreParticipantData(store, game, format, date_start, date_end)
  if len(participant_data) == 0:
    message += 'No participant data found for this store.'
  else:  
    header = 'GAME,FORMAT,DATE,PLAYER_NAME,ARCHETYPE_PLAYED,WINS,LOSSES,DRAWS'
    files.append(ConvertRowsToFile(participant_data, 'MyStoreParticipantData', header))
    message += ' Participant data is attached.'

  round_data = GetStoreRoundData(store, game, format, date_start, date_end)
  if len(round_data) == 0:
    message += 'No round by round data found for this store.'
  else:
    header = 'GAME,FORMAT,DATE,ROUND,PLAYER_NAME,ARCHETYPE_PLAYED,OPPONENT_NAME,OPPONENT_ARCHETYPE,RESULT'
    files.append(ConvertRowsToFile(round_data, 'MyStoreRoundByRoundData', header))
    message += ' Round by round data is attached.'
    
  return message, files

def GetPlayerData(interaction, start_date, end_date):
  game, format, store, user_id = GetInteractionData(interaction, store=True, game=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  
  message = f'Here is your data for {store.StoreName.title()}:'
  files = []

  print('Getting participant data')
  participant_data = GetPlayerParticipantData(store, game, format, date_start, date_end, user_id)
  if len(participant_data) == 0:
    print('No participant data found')
    message += 'No participant data found for this player.'
  else:
    print('Participant data found')
    header = 'GAME,FORMAT,DATE,ARCHETYPE_PLAYED,WINS,LOSSES,DRAWS'
    files.append(ConvertRowsToFile(participant_data, 'MyStoreParticipantData', header))

  print('Getting round data')
  round_data = GetPlayerRoundData(store, game, format, date_start, date_end, user_id)
  if len(round_data) == 0:
    print('No round data found')
    message += 'No round by round data found for this player.'
  else:
    print('Round data found')
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
  