from tuple_conversions import Participant, Round
from data_conversions.lorcana_official import LorcanaOfficialRound, LorcanaOfficialParticipant

def ConvertMessageToData(message):
  data = CompanionParticipants(message)
  if data is None:
    data = MeleeParticipants(message)
  if data is None:
    data = CompanionRoundByRound(message)
  if data is None:
    data = CompanionParticipantsWithTabs(message)
  '''Cannot determine what round this is
  if data is None:
    data = LorcanaOfficialRound(message)
  '''
  if data is None:
    data = LorcanaOfficialParticipant(message)
  return data

def CompanionParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for row in rows:
      row_list = row.split('    ')
      int(row_list[0]) #Standing
      int(row_list[2]) #Points obtained
      record = row_list[3].split('/')
      player_name = row_list[1]
      participant = Participant(player_name,
                                int(record[0]),
                                int(record[1]),
                                int(record[2]))
      data.append(participant)
    return data
  except Exception as exception:
    #print('Rows:', rows)
    #print('Companion Participants Exception:', exception)
    return None

def CompanionParticipantsWithTabs(message):
  data = []
  rows = message.split('\n')
  try:
    for row in rows:
      row_list = row.split('\t')
      int(row_list[0]) #Standing
      int(row_list[2]) #Points obtained
      record = row_list[3].split('/')
      player_name = row_list[1]
      participant = Participant(player_name,
                                int(record[0]),
                                int(record[1]),
                                int(record[2]))
      data.append(participant)
    return data
  except Exception as exception:
    print('Rows:', rows)
    print('Companion Participants With Tabs Exception:', exception)
    return None

def MeleeParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 3):
      name = ' '.join(rows[i + 1].split(' ')[0:-1])
      record = rows[i + 2].split('    ')[0].split('-')
      participant = Participant(name,
                                int(record[0]),
                                int(record[1]),
                                int(record[2]))
      data.append(participant)
    return data
  except Exception as exception:
    print('Rows:', rows)
    print('Melee Participants Exception:', exception)
    return None

def CompanionRoundByRound(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 6):
      row = rows[i:i + 6]
      if row[3] != 'Bye':
        p1name = row[1]
        p1gw = row[3][0]
        p2gw = row[3][1]
        p2name = row[4]
        roundnumber = int(row[2][0])+ int(row[2][2])+int(row[2][4])
        result = Round(p1name, p1gw, p2name, p2gw, roundnumber)
        data.append(result)
      else:
        p1name = row[0]
        p1gw = 2
        p2name = 'Bye'
        p2gw = 0
        roundnumber = int(row[1][0])+int(row[1][2])+int(row[1][4])
        result = Round(p1name, p1gw, p2name, p2gw, roundnumber)
        data.append(result)
    return data
  except Exception as exception:
    print('Rows:', rows)
    print('Companion Round Exception:', exception)
    return None

'''
TODO: League data
I would like to receive data meant for leagues and digest it into the database
What I need to be reported is the match number, the players' names, the players' archetype, and each player's game win count
ObjReceived(match_number, player1_name, player1_archetype, player1_game_wins, player2_name, player2_archetype, player2_game_wins)
Most likely this will need to go into the rounds table and the archetype table
Issue is though, how do I link the correct archetype to the correct player and the correct match, because archetypes are currently linked to event_id and player_name.
I may need to add a new table and condense the data into another view
'''