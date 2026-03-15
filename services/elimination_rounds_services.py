from typing import Tuple
from data.elimination_rounds_data import GetEliminationPairings, GetEliminationStandings
from tuple_conversions import Event, ReportedAs

def GetEliminationRoundData(event:Event) -> str:
  title = f"{event.event_date.strftime("%m/%d/%Y")} - {event.event_name}'s Top 8:"
  output = ''
 
  #If the selected tournament is submitted via standings, obtain the top 8 that way
  if event.reported_as == ReportedAs.Standings.value:
    data = GetEliminationStandings(event)
    output = BuildEliminationStandingOutput(data)
  #If the selected tournament is submitted via pairings, obtain the top 8 that way
  elif event.reported_as == ReportedAs.Pairings.value:
    data = GetEliminationPairings(event)
    output = BuildEliminationPairingOutput(data)

  output = f'```{title}\n{output}```'
  
  return output

def BuildEliminationStandingOutput(data: list[Tuple[int, str, int, str, int]]) -> str:
  """Builds the output for the elimination rounds when the event is submitted via standings"""
  output = f'''
Winner:
  {data[0][0]}
  
Runner Up:
  {data[1][0]}
  
Semifinalists:
  {data[2][0]}
  {data[3][0]}
'''

  if len(data) > 4:
    output += f'''
Quarterfinalists:
  {data[4][0]}
  {data[5][0]}
  {data[6][0]}
  {data[7][0]}'''
  return output

def BuildEliminationPairingOutput(data: list[Tuple[int, str, int, str, int]]) -> str:
  """Builds the output for the elimination rounds when the event is submitted via pairings"""
  output = ''

  if len(data) > 3:
    output = Top8(data)
  else:
    output = Top4(data)
  
  return output

def Top8(data: list[Tuple[int, str, int, str, int]]) -> str:
  """Determining outcomes based upon the data from the top 8"""
  output = ''
  draws = CountDraws(data)
  
  if len(data) == 7:
    finals = ''
    if draws == 1:
      finals = f'{data[0][1]} drew with {data[0][3]}'
    elif data[0][2] > data[0][4]:
      finals = f'{data[0][1]} defeated {data[0][3]}'
    else:
      finals = f'{data[0][3]} defeated {data[0][1]}'
    
    output = f'''
Finals:
  {finals}
  
Semifinals:
  {data[1][1]} defeated {data[1][3]}
  {data[2][1]} defeated {data[2][3]}
  
Quarterfinals:
  {data[3][1]} defeated {data[3][3]}
  {data[4][1]} defeated {data[4][3]}
  {data[5][1]} defeated {data[5][3]}
  {data[6][1]} defeated {data[6][3]}'''

  elif len(data) == 6:
    output = f'''
Semifinals:
  {data[0][1]} drew with {data[0][3]}
  {data[1][1]} drew with {data[1][3]}

Quarterfinals:
  {data[2][1]} defeated {data[2][3]}
  {data[3][1]} defeated {data[3][3]}
  {data[4][1]} defeated {data[4][3]}
  {data[5][1]} defeated {data[5][3]}'''

  elif len(data) == 4:
    output = f'''
Quarterfinals:
  {data[0][1]} drew with {data[0][3]}
  {data[1][1]} drew with {data[1][3]}
  {data[2][1]} drew with {data[2][3]}
  {data[3][1]} drew with {data[3][3]}'''

  return output
  

def Top4(data: list[Tuple[int, str, int, str, int]]) -> str:
  """Determining outcomes based upon the data from the top 4"""
  output = ''
  draws = CountDraws(data)

  if len(data) == 3:
    finals = ''
    if draws == 1:
      finals = f'{data[0][1]} drew with {data[0][3]}'
    elif data[0][2] > data[0][4]:
      finals = f'{data[0][1]} defeated {data[0][3]}'
    else:
      finals = f'{data[0][3]} defeated {data[0][1]}'

    output = f'''
Finals:
  {finals}

Semifinals:
  {data[1][1]} defeated {data[1][3]}
  {data[2][1]} defeated {data[2][3]}'''

  else:
    output = f'''
Semifinals:
  {data[0][1]} drew with {data[0][3]}
  {data[1][1]} drew with {data[1][3]}'''
  
  return output

def CountDraws(data: list[Tuple[int, str, int, str, int]]) -> int:
  draws = 0
  for row in data:
    if row[2] == row[4]:
       draws += 1

  return draws