from collections import namedtuple

MetagameRow = namedtuple('MetagameRow', ['Archetype',
                                         'MetagamePer',
                                         'WinPer',
                                         'CombinedRank'])

TopPlayerRow = namedtuple('TopPlayerRow', ['PlayerName',
                                           'MetagamePer',
                                           'WinPer',
                                           'CombinedPer'])

Event = namedtuple('Event', ['ID',
                             'EventDate',
                             'LocationDiscordID',
                             'GameID',
                             'FormatID'])

Participant = namedtuple('Participant', ['PlayerName',
                                         'Wins',
                                         'Losses',
                                         'Draws'])

Format = namedtuple('Format', ['ID',
                               'FormatName'])

Game = namedtuple('Game', ['ID',
                           'Name'])

Store = namedtuple('Store', ['DiscordId',
                             'DiscordName',
                             'StoreName',
                             'OwnerId',
                             'OwnerName',
                             'ApprovalStatus'])

def ConvertToEvent(event_obj):
  return Event(event_obj[0],
               event_obj[1],
               event_obj[2],
               event_obj[3],
               event_obj[4])

def ConvertToParticipant(participant_obj):
  return Participant(participant_obj[0],
                     participant_obj[1],
                     participant_obj[2],
                     participant_obj[3],
                     participant_obj[4],
                     participant_obj[5],
                     participant_obj[6],
                     participant_obj[7])  

def ConvertToStore(store):
  return Store(int(store[0]),
               store[1],
               store[2],
               int(store[3]),
               store[4],
               store[5])

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
                                    ConvertDecimalToPercentStr(dataRows[i][1]),
                                    ConvertDecimalToPercentStr(dataRows[i][2]),
                                    ConvertDecimalToPercentStr(dataRows[i][3])))

  return top_players

def ChangeDataToMetagame(rows):
  filtered_rows = []
  for i in range(len(rows)):
    if rows[i][1] > .02:
      filtered_rows.append(MetagameRow(rows[i][0].title(),
                                       ConvertDecimalToPercentStr(rows[i][1]),
                                       ConvertDecimalToPercentStr(rows[i][2]),
                                       ConvertDecimalToPercentStr(rows[i][3])))

  return filtered_rows

#This isn't done with a built in function due to BuildOutput not knowing types
def ConvertDecimalToPercentStr(number): 
  percent = round(number * 100, 2)
  str_percent = '{:.2f}%'.format(percent)
  return str_percent