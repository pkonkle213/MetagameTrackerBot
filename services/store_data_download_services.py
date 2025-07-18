from discord import File
from io import BytesIO
from services.date_functions import BuildDateRange
from data.store_data import GetStoreData
from interaction_data import GetInteractionData

def GetDataReport(interaction, start_date, end_date):
  game, format, store, user_id = GetInteractionData(interaction, store=True, game=True)
  date_start, date_end = BuildDateRange(start_date, end_date, format)
  data = GetStoreData(store, game, format, date_start, date_end)
  if len(data) == 0:
    return None, None
  header = 'GAME,FORMAT,DATE,PLAYER_NAME,ARCHETYPE_PLAYED,WINS,LOSSES,DRAWS'
  file = ConvertRowsToFile(data, 'MyStoreData', header)
  message = f'Here is the data for {store.StoreName.title()}'
  return message, file

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