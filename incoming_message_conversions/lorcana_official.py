import pandas as pd
from tuple_conversions import Pairing, Standing, Result

#TODO: This may be out of date and needs updated as Lorcana has CSV export
def LorcanaOfficialPairing(dataframe:pd.DataFrame):
  """Takes a provided dataframe and attempts to make it into a Pairing object"""
  data = []
  errors = []
  
  try:
    #TODO: I don't know what a bye looks like in the CSV
    for index, row in dataframe.iterrows():
      p1name = row['Player 1 First Name'] + ' ' + row['Player 1 Last Name']
      p2name = row['Player 2 First Name'] + ' ' + row['Player 2 Last Name']
      p1gw = row['Player 1 Round Record'][0]
      p2gw = row['Player 2 Round Record'][0]
      result = Pairing(p1name, p1gw, p2name, p2gw, 0)
      data.append(result)    
    
    return Result(data if len(data) > 0 else None, errors)
    
  except Exception as exception:
    print('Lorcana Official Pairing DataFrame:', dataframe)
    print('Lorcana Official Pairing Exception:', exception)
    return Result(None, None)

#TODO: This may be out of date and needs updated
def LorcanaOfficialStanding(dataframe:pd.DataFrame):
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

    return Result(data if len(data) > 0 else None, errors)
  except Exception as exception:
    print('Lorcana Official Standing Rows:', dataframe)
    print('Lorcana Official Standing Exception:', exception)
    return Result(None, None)