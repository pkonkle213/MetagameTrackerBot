from tuple_conversions import Round, Participant

def LorcanaOfficialRound(message):
  data = []
  rows = message.split('\n')
  try:
    start = 0
    if rows[7].upper() == 'BYE':
      data.append(Round(rows[1].upper(), 2, 'BYE', 0, 0))
      start = 8
    for i in range(start, len(rows), 9):
      row = rows[i:i + 9]
      p1name = row[1]
      p2name = row[3]
      colon = row[7].index(':')
      p1gw = row[7][colon + 2]
      p2gw = row[7][colon + 4]
      result = Round(p1name, p1gw, p2name, p2gw, 0) #TODO: How do I figure out what round it is?
      data.append(result)
    return data
  except Exception as exception:
    print('Lorcana Official Round Rows:', rows)
    print('Lorcana Official Round Exception:', exception)
    return None

def LorcanaOfficialParticipant(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 4):
      row = rows[i:i + 4]
      name = row[1]
      details = row[3].split('    ')
      wins = details[2][0]
      losses = details[2][2]
      draws = details[2][4]
      participant = Participant(name,
                                wins,
                                losses,
                                draws)
      print('Participant: ', participant)
      data.append(participant)
    return data
  except Exception as exception:
    print('Lorcana Official Participant Rows:', rows)
    print('Lorcana Official Participant Exception:', exception)