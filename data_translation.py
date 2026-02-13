from typing import Tuple
import pandas as pd
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.csv_carde_io import ConvertToPairings, ConvertToStandings
from tuple_conversions import Game, Pairing, Standing

def ConvertCSVToData(
  dataframe:pd.DataFrame,
  game:Game
) -> Tuple[list[Standing] | list[Pairing], list[str]]:
  data = None
  errors = []
  if data is None:
    data, errors = ConvertToPairings(dataframe)

  if data is None:
    data, errors = ConvertToStandings(dataframe)

  if not data:
    raise Exception("Unable to parse data. Please try again.")
  return data, errors  

def ConvertMessageToData(
  message:str,
  game:Game
) -> Tuple[list[Pairing] | list[Standing], list[str], int]:
  data = None
  errors = []
  if game.GameName.upper() == 'MAGIC':
    print('Attempting to parse Magic - Companion Data')
    
    if data is None:
      print('Testing magic - companion - standings - 4 spaces')
      data, errors = CompanionStandings(message, "    ")
      round_number = 0
    
    if data is None:
      print('Testing magic - companion - standings - tab')
      data, errors = CompanionStandings(message, "\t")
      round_number = 0
    
    if data is None:
      print('Testing magic - companion - pairings')
      data, errors, round_number = CompanionPairings(message)

  if not data:
    raise Exception("Unable to parse data. Please try again.")
    
  return data, errors, round_number
