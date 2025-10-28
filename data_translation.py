import pandas as pd
from discord import Interaction
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.lorcana_official import LorcanaOfficialPairing, LorcanaOfficialStanding
from incoming_message_conversions.melee import MeleeStandings, MeleePairings
from tuple_conversions import Game

def ConvertCSVToData(interaction:Interaction,
                     dataframe:pd.DataFrame,
                     game:Game):
  data = None
  errors = []
  if game.Name.upper() == 'LORCANA':
    if data is None:
      data, errors = LorcanaOfficialPairing(dataframe)

    if data is None:
      data, errors = LorcanaOfficialStanding(dataframe)

  """
  if game.Name.upper() == 'STAR WARS UNLIMITED':
    if data is None:
      data, errors = StarWarsOfficialPairing(csv_file)

    if data is None:
      data, errors = StarWarsOfficialStanding(csv_file)
  """
  
  return data, errors  

def ConvertMessageToData(interaction:Interaction,
                         message:str,
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

  if data is None:
    print('Attempting to parse Melee Standings Data')
    data, errors = MeleeStandings(message)

  if data is None:
    print('Attempting to parse Melee Pairings Data')
    data, errors = MeleePairings(message)
  
  return data, errors
