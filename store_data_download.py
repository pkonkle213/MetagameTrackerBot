from discord import File
from io import BytesIO
from date_functions import ConvertToDate, GetToday
from database_connection import GetStoreData


def GetDataReport(discord_id, start_date, end_date):
  date_start = ConvertToDate(start_date if start_date != '' else '1/1/2024')
  date_end = ConvertToDate(end_date) if end_date != '' else GetToday()
  data = GetStoreData(discord_id, date_start, date_end)
  if len(data) == 0:
    return None
  header = 'GAME,FORMAT,DATE,PLAYER_NAME,ARCHETYPE_PLAYED,WINS,LOSSES,DRAWS'
  file = ConvertRowsToFile(data, 'MyStoreData', header)
  return file

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