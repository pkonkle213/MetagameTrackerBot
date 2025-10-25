from tuple_conversions import Pairing, Standing

#TODO: This may be out of date and needs updated as Lorcana has CSV export
def LorcanaOfficialPairing(message):
  data = []
  rows = message.split('\n')
  table_length = 18
  try:
    start = 0
    #TODO: I think this could be a while loop in case the RARE event that there is more than one BYE
    if rows[7].upper() == 'BYE':
      #TODO: This probably needs updated too
      pairing = Pairing(rows[1], 2, 'BYE', 0, 0)
      data.append(pairing)
      start = 8
    for i in range(start, len(rows), table_length):
      row = rows[i:i + table_length]
      print('Lorcana Official Pairing Row:', row)
      p1name = row[1] #But it's LASTNAME, FIRSTNAME
      p2name = row[4] #But it's LASTNAME, FIRSTNAME
      record_index = 8
      record_split = row[record_index].index(',')
      p1gw = row[record_index][record_split + 2]
      p2gw = row[record_index][record_split + 4]
      result = Pairing(p1name, p1gw, p2name, p2gw, 0)
      print('Lorcana Official Pairing Result:', result)
      data.append(result)
    return data
  except Exception as exception:
    print('Lorcana Official Pairing Rows:', rows)
    print('Lorcana Official Pairing Exception:', exception)
    return None

#TODO: This may be out of date and needs updated
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