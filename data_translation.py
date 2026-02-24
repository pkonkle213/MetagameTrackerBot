from typing import Tuple
import pandas as pd
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.csv_carde_io import ConvertToPairings, ConvertToStandings
from tuple_conversions import Game, Pairing, Standing

def ConvertCSVToData(
  dataframe:pd.DataFrame,
  game:Game
) -> Tuple[list[Standing] | None, list[Pairing] | None, list[str] | None]:
  errors = None
  standings_data = None
  pairings_data = None
  
  pairings_data, errors = ConvertToPairings(dataframe)

  if pairings_data is None:
    standings_data, errors = ConvertToStandings(dataframe)

  if pairings_data is None and standings_data is None:
    raise Exception("Unable to parse data. Please try again.")
  return standings_data, pairings_data, errors

def ConvertMessageToData(
  message:str,
  game:Game
) -> Tuple[list[Standing] | None, list[Pairing] | None, list[str] | None, int]:
  errors = None
  round_number = 0
  standings_data = None
  pairings_data = None
  
  if game.GameName.upper() == 'MAGIC':
    #magic - companion - standings - 4 spaces
    standings_data, errors = CompanionStandings(message, "    ")
    
    if standings_data is None:
      #magic - companion - standings - tab
      standings_data, errors = CompanionStandings(message, "\t")
    
    if standings_data is None:
      #magic - companion - pairings
      pairings_data, errors, round_number = CompanionPairings(message)

  if standings_data is None and pairings_data is None:
    raise Exception("Unable to parse data. Please try again.")
    
  return standings_data, pairings_data, errors, round_number
