import pandas as pd
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.csv_carde_io import Pairings, Standings
from tuple_conversions import Game

def ConvertCSVToData(dataframe:pd.DataFrame,
                     game:Game):
  data = None
  errors = []
  if data is None:
    data, errors = Pairings(dataframe)

  if data is None:
    data, errors = Standings(dataframe)
  
  return data, errors  

def ConvertMessageToData(message:str,
                         game:Game):
  data = None
  errors = []
  if game.Name.upper() == 'MAGIC':
    print('Attempting to parse Magic - Companion Data')
    
    if data is None:
      print('Testing magic - companion - standings - 4 spaces')
      data, errors = CompanionStandings(message, "    ")
        
    if data is None:
      print('Testing magic - companion - standings - tab')
      data, errors = CompanionStandings(message, "\t")
    
    if data is None:
      print('Testing magic - companion - pairings')
      data, errors = CompanionPairings(message)
  
  return data, errors
