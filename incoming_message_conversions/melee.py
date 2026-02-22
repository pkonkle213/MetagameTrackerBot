import pytz
from datetime import datetime
from tuple_conversions import Pairing

def MeleeJsonPairings(json_data:list) -> tuple[list[Pairing], list[str], int, str, dict[str,str]]:
  data = []
  errors = []
  archetypes = {}

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
      p1archetype = DetermineAchetype(match['Competitors'][0])
      if archetypes.get(p1name) is None and p1archetype:
        print('Adding archetype for player 1:', p1name, p1archetype)
        archetypes[p1name] = p1archetype
      if p1byes > 0:
        p2name = 'BYE'
        p2gw = 0
      else:
        p2name = match['Competitors'][1]['Team']['Players'][0]['Name']
        p2gw_obj = match['Competitors'][1]['GameWins']
        p2gw = int(p2gw_obj) if p2gw_obj else 0
        p2archetype = DetermineAchetype(match['Competitors'][1])
        if archetypes.get(p2name) is None and p2archetype:
          print('Adding archetype for player 2:', p2name, p2archetype)
          archetypes[p2name] = p2archetype
      pairing = Pairing(p1name, p1gw, p2name, p2gw, round_number)
            
      data.append(pairing)
    except Exception as e:
      errors.append(f'Unable to parse round {round_number}, table number {table_number} match due to {e}')
    
  return data, errors, 0, event_date, archetypes

def DetermineAchetype(competitor: dict) -> str | None:
  decklists = competitor['Decklists'][0]
  if len(decklists) == 0:
    print('No decklist found')
    return None

  name = decklists['DecklistName']
  return name
  