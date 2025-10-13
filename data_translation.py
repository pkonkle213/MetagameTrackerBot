from discord import Interaction
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.lorcana_official import LorcanaOfficialPairing, LorcanaOfficialStanding
from incoming_message_conversions.melee import MeleeStandings, MeleePairings
from tuple_conversions import Game

def ConvertMessageToData(interaction:Interaction,
                         message:str,
                         game:Game):
  data = None
  errors = []
  if game.Name.upper() == 'MAGIC':
    if data is None:
      data, errors = CompanionStandings(message, "    ")
        
    if data is None:
      data, errors = CompanionStandings(message, "\t")
    
    if data is None:
      data, errors = CompanionPairings(message)

  if data is None:
    print('Attempting to parse Melee Standings Data')
    data, errors = MeleeStandings(message)

  if data is None:
    print('Attempting to parse Melee Pairings Data')
    data, errors = MeleePairings(message)

  '''
  if game is not None and game.Name == 'Lorcana':
    #Cannot determine what round this is
    if data is None:
      data = LorcanaOfficialPairing(message)
    if data is None:
      data = LorcanaOfficialStanding(message)
  '''
  
  return data, errors
