from tuple_conversions import Participant, Round

def ConvertMessageToParticipants(message):
  data = CompanionParticipants(message)
  if data is None:
    data = MeleeParticipants(message)
  if data is None:
    data = CompanionRoundByRound(message)
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
      participant = Participant(row_list[1].encode('ascii', 'ignore').decode('ascii'),
                                int(record[0]),
                                int(record[1]),
                                int(record[2]))
      data.append(participant)
    return data
  except Exception as exception:
    #print('Rows:', rows)
    #print('Companion Participants Exception:', exception)
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
    #print('Rows:', rows)
    #print('Melee Participants Exception:', exception)
    return None

def CompanionRoundByRound(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 6):
      row = rows[i:i + 6]
      #print('Row:', row)
      if row[3] != 'Bye':
        p1name = row[1].encode('ascii', 'ignore').decode('ascii')
        p1gw = row[3][0]
        p2gw = row[3][1]
        p2name = row[4]
        result = Round(p1name, int(p1gw), p2name, int(p2gw))
        #print('Result:', result)
        data.append(result)
      if row[3] == 'Bye':
        p1name = row[0].encode('ascii', 'ignore').decode('ascii')
        p1gw = 2
        p2name = 'Bye'
        p2gw = 0
        result = Round(p1name, int(p1gw), p2name, int(p2gw))
        #print('Result:', result)
        data.append(result)
    return data
  except Exception as exception:
    #print('Rows:', rows)
    #print('Companion Round Exception:', exception)
    return None