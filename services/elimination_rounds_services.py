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

#TODO: This needs to take into account draws
def BuildEliminationStandingOutput(data: list[Tuple[str, int, int, int]]) -> str:
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

#TODO: This needs to take into account draws
def BuildEliminationPairingOutput(data: list[Tuple[int, str, str, str]]) -> str:
  """Builds the output for the elimination rounds when the event is submitted via pairings"""
  output = f'''
Finals:
  {data[0][1]} defeats {data[0][2]}
  
Semifinals:
  {data[1][1]} defeats {data[1][2]}
  {data[2][1]} defeats {data[2][2]}
'''
  if len(data) > 4:
    output += f'''
Quarterfinals:
  {data[3][1]} defeats {data[3][2]}
  {data[4][1]} defeats {data[4][2]}
  {data[5][1]} defeats {data[5][2]}
  {data[6][1]} defeats {data[6][2]}'''
  return output