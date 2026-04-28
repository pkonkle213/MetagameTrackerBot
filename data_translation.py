from typing import Tuple
import pandas as pd
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.csv_carde_io import ConvertToPairings, ConvertToStandings
from tuple_conversions import Game, Pairing, Standing, DataConverted, GameEnum

def ConvertCSVToData(
  dataframe:pd.DataFrame,
) -> DataConverted:
  errors = None
  standings_data = None
  pairings_data = None
  
  pairings_data, errors = ConvertToPairings(dataframe)

  if pairings_data is None:
    standings_data, errors = ConvertToStandings(dataframe)

  if pairings_data is None and standings_data is None:
    raise Exception("Unable to parse data. Please try again.")

  return DataConverted(
    pairings_data,
    standings_data,
    errors,
    None,
    None,
    None,
    None
  )

def ConvertMessageToData(
  message:str,
  gameId:int
) -> DataConverted:
  errors = None
  round_number = 0
  standings_data = None
  pairings_data = None
  
  if gameId == GameEnum.Magic.value:
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

  return DataConverted(
    pairings_data,
    standings_data,
    errors,
    round_number,
    None,
    None,
    None
  )
