import pytz
from datetime import datetime
from tuple_conversions import Standing, Pairing, Result

def MeleeJsonPairings(json_data) -> tuple[list[Pairing], list[str], str, str]:
  data = []
  errors = []

  date_created = json_data[0]['DateCreated']
  date_string = datetime.fromisoformat(date_created)
  est = pytz.timezone('US/Eastern')
  event_date = date_string.astimezone(est).strftime('%m/%d/%Y')
  
  for match in json_data:
    round_number = int(match['RoundDescription'][6:])
    table_number = match['TableNumber'] if match['TableNumber'] else 'Bye'
    try:
      p1name = match['Competitors'][0]['Team']['Players'][0]['Name']
      p1gw_obj = match['Competitors'][0]['GameWins']
      p1gw = int(p1gw_obj) if p1gw_obj else 2
      p1byes = int(match['Competitors'][0]['GameByes'])
      if p1byes > 0:
        p2name = 'BYE'
        p2gw = 0
      else:
        p2name = match['Competitors'][1]['Team']['Players'][0]['Name']
        p2gw_obj = match['Competitors'][1]['GameWins']
        #TODO: I don't like this, but somehow this data has null for p2gw
        p2gw = int(p2gw_obj) if p2gw_obj else 0 
      pairing = Pairing(p1name, p1gw, p2name, p2gw, round_number)
      data.append(pairing)
    except Exception as e:
      errors.append(f'Unable to parse round {round_number}, table number {table_number} match due to {e}')
    
  return data, errors, '', event_date

#TODO: This will be updated soon, once CSV files are obtained
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

def MeleePairings(message):
  data = []
  errors = []
  rows = message.split('\n')
  byes = True
  
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
      if winner == p1name:
        wins = record[0]
        losses = record[1]
      else:
        wins = record[1]
        losses = record[0]
      
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
    