from typing import Tuple
import pandas as pd
from tuple_conversions import Pairing, Standing

def ConvertToPairings(dataframe:pd.DataFrame) -> Tuple[list[Pairing] | None, list[str] | None]:
  """Takes a provided dataframe and attempts to make it into a Pairing object"""
  data = []
  errors = []
  
  try:
    for index, row in dataframe.iterrows():
      if row['Table Number'] == -1:
        p1name = row['Player 1 First Name'] + ' ' + row['Player 1 Last Name']
        p2name = 'Bye'
        p1gw = 2
        p2gw = 0
      else:
        p1name = row['Player 1 First Name'] + ' ' + row['Player 1 Last Name']
        p2name = row['Player 2 First Name'] + ' ' + row['Player 2 Last Name']
        p1gw = row['Player 1 Round Record'][0]
        p2gw = row['Player 2 Round Record'][0]
      result = Pairing(p1name, p1gw, p2name, p2gw, 0)
      data.append(result)    
    
    return data if len(data) > 0 else None, errors
    
  except Exception as exception:
    print('Carde.io Pairing DataFrame:\n', dataframe)
    print('Carde.io Official Pairing Exception:', exception)
    return None, None

def ConvertToStandings(dataframe:pd.DataFrame) -> Tuple[list[Standing] | None, list[str] | None]:
  """Takes a provided dataframe and attempts to make it into a Standing object"""
  data = []
  errors = []
  try:
    for index, row in dataframe.iterrows():
      name = row['Name']
      record = row['Record']
      wins = record[0]
      losses = record[2]
      draws = record[4]
      participant = Standing(name,
                             wins,
                             losses,
                             draws)
      data.append(participant)

    return data if len(data) > 0 else None, errors
  except Exception as exception:
    print('Lorcana Official Standing Rows:\n', dataframe)
    print('Lorcana Official Standing Exception:', exception)
    return None, None