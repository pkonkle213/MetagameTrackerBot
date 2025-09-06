from tuple_conversions import Pairing, Standing

def LorcanaOfficialPairing(message):
  data = []
  rows = message.split('\n')
  try:
    start = 0
    if rows[7].upper() == 'BYE':
      data.append(Pairing(rows[1].upper(), 2, 'BYE', 0, 0))
      start = 8
    for i in range(start, len(rows), 9):
      row = rows[i:i + 9]
      p1name = row[1]
      p2name = row[3]
      colon = row[7].index(':')
      p1gw = row[7][colon + 2]
      p2gw = row[7][colon + 4]
      result = Pairing(p1name, p1gw, p2name, p2gw, 0)
      data.append(result)
    return data
  except Exception as exception:
    print('Lorcana Official Pairing Rows:', rows)
    print('Lorcana Official Pairing Exception:', exception)
    return None

def LorcanaOfficialStanding(message):
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
      participant = Standing(name,
                                wins,
                                losses,
                                draws)
      print('Participant: ', participant)
      data.append(participant)
    return data
  except Exception as exception:
    print('Lorcana Official Standing Rows:', rows)
    print('Lorcana Official Standing Exception:', exception)