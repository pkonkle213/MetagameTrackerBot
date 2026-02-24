from typing import Tuple
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
    print('Match:\n', match)
    round_number = match['RoundNumber']
    try:
      if match['TableNumber']:
        pairing, player_archetypes = PairedMatch(match)
        archetypes = archetypes | player_archetypes
      else:
        pairing, player_archetypes = ByeMatch(match)
        archetypes = archetypes | player_archetypes        
      
      data.append(pairing)
    except Exception as e:
      errors.append(f'Unable to parse round {round_number}, due to {e}')
  return data, errors, 0, event_date, archetypes

def ByeMatch(match: dict) -> Tuple[Pairing, dict[str,str | None]]:
  print('Bye match:\n', match)
  p1name = match['Competitors'][0]['Team']['Players'][0]['Name']
  p1gw = match['Competitors'][0]['GameByes']
  p1archetype = DetermineAchetype(match['Competitors'][0])
  p2name = 'BYE'
  p2gw = 0
  round_number = match['RoundNumber']
  pairing = Pairing(p1name, p1gw, p2name, p2gw, round_number)
  print('Bye match paired:\n', pairing)
  return pairing, {p1name: p1archetype}

def PairedMatch(match: dict) -> Tuple[Pairing, dict[str,str | None]]:
  print('Paired match:\n', match)
  p1name = match['Competitors'][0]['Team']['Players'][0]['Name']
  p1gw = match['Competitors'][0]['GameWins'] if match['Competitors'][0]['GameWins'] else 0
  p1archetype = DetermineAchetype(match['Competitors'][0])
  p2name = match['Competitors'][1]['Team']['Players'][0]['Name']
  p2gw = match['Competitors'][1]['GameWins'] if match['Competitors'][1]['GameWins'] else 0
  p2archetype = DetermineAchetype(match['Competitors'][1])
  round_number = match['RoundNumber']
  
  pairing = Pairing(p1name, p1gw, p2name, p2gw, round_number)
  print('Paired match, paired:\n', pairing)
  return pairing, {p1name: p1archetype, p2name:p2archetype}

def DetermineAchetype(competitor: dict) -> str | None:
  decklists = competitor['Decklists']
  if len(decklists) == 0:
    print('No decklist found')
    return None

  name = decklists['DecklistName'] #TODO: Does this work!?
  return name
  