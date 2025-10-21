from tuple_conversions import Standing, Pairing, Result

#TODO: If this includes the "decklist" column, that adds a row to each standing
def MeleeStandings(message):
  data = []
  errors = []
  rows = message.split('\n')

  for i in range(0, len(rows), 3):
    try:
      row = rows[i:i+3]
      name = SeperateNameFromPronouns(row[1])
      stats = row[2].split(' ')
      match_record = stats[0].split('-')
      wins = int(match_record[0])
      losses = int(match_record[1])
      draws = int(match_record[2])
  
      standing = Standing(name, wins, losses, draws)
      print('Standing:', standing)
      
      data.append(Standing(name, wins, losses, draws))
    except Exception as e:
      errors.append(f'Unable to parse row(s) {i+1} - {i+3} due to {e}')
  
  return Result(data if len(data) > 0 else None, errors)

#TODO: If this includes the "decklist" column, that adds a row to each standing
def MeleePairings(message):
  data = []
  errors = []
  rows = message.split('\n')
  byes = True
  
  #TODO: Start looking for byes, which have 3-4 rows
  i = 0
  while byes:
    if rows[i + 2].split(' ')[-1] == 'bye':
      row = rows[i:i+3]
      p1name = SeperateNameFromPronouns(row[1]).strip()
      p2name = 'BYE'
      wins = 2
      losses = 0
      round_number = 0
      pairing = Pairing(p1name, wins, p2name, losses, round_number)
      print('Bye Pairing:', pairing)
      data.append(pairing)
      i += 3
    else:
      byes = False
    
  for j in range(i, len(rows), 4):
    try:
      row = rows[j:j+4]
      p1name = SeperateNameFromPronouns(row[1]).strip()
      p2name = SeperateNameFromPronouns(row[2]).strip()
      winner = ' '.join(row[3].split(' ')[:-2]).strip()
      record = row[3].split(' ')[-1].split('-')
      print('Comparison:', winner == p1name)
      if winner == p1name:
        wins = record[0]
        losses = record[1]
      else:
        wins = record[1]
        losses = record[0]
      print('WLD', wins, losses)
      
      pairing = Pairing(p1name, wins, p2name, losses, 0)
      data.append(pairing)
    except Exception as e:
      errors.append(f'Unable to parse row(s) {j+1} - {j+4} due to {e}')

  return Result(data if len(data) > 0 else None, errors)

def SeperateNameFromPronouns(name_pro):
  elements = name_pro.strip().split(' ')
  if '/' in elements[-1]:
    return ' '.join(elements[:-1])
  else:
    return name_pro
    