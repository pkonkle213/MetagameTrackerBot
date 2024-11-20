from collections import namedtuple

MetagameRow = namedtuple('MetagameRow', ['Archetype',
         'MetagamePer',
         'WinPer',
         'CombinedRank'])

TopPlayerRow = namedtuple('TopPlayerRow', ['PlayerName',
                                           'MetagamePer',
                                           'WinPer',
                                           'CombinedPer'])

DataRow = namedtuple('DataRow', ['DateOfEvent',
                                 'LocationDiscordId',
                                 'GamePlayed',
                                 'Format',
                                 'PlayerName',
                                 'ArchetypePlayed',
                                 'Wins',
                                 'Losses',
                                 'Draws',
                                 'SubmitterId'])

Store = namedtuple('Store', ['Name',
                             'DiscordId',
                             'DiscordName',
                             'Owner',
                             'ApprovalStatus'])

def ConvertToStore(store):
  return Store(store[0],
               int(store[1]),
               store[2],
               int(store[3]),
               store[4])

def ConvertToDataRow(result):
  return DataRow(result[0],
                 int(result[1]),
                 result[2].upper(),
                 result[3].upper(),
                 result[4].upper(),
                 result[5].upper(),
                 int(result[6]),
                 int(result[7]),
                 int(result[8]),
                 int(result[9]))

def ChangeDataRowsToLeaderBoard(dataRows):
  top_players = []
  for i in range(len(dataRows)):
    top_players.append(TopPlayerRow(dataRows[i][0].title(),
                                    ConvertToPercentStr(dataRows[i][1]),
                                    ConvertToPercentStr(dataRows[i][2]),
                                    ConvertToPercentStr(dataRows[i][3])))

  return top_players

def ChangeDataToMetagame(rows):
  filtered_rows = []
  for i in range(len(rows)):
    if rows[i][1] > .02:
      filtered_rows.append(MetagameRow(rows[i][0].title(),
                                       ConvertToPercentStr(rows[i][1]),
                                       ConvertToPercentStr(rows[i][2]),
                                       ConvertToPercentStr(rows[i][3])))

  return filtered_rows

def ConvertToPercentStr(number):
  percent = round(number * 100, 2)
  str_percent = '{:.2f}%'.format(percent)
  return str_percent