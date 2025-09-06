from discord import Interaction
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.lorcana_official import LorcanaOfficialPairing, LorcanaOfficialStanding
from tuple_conversions import Game

def ConvertMessageToData(interaction:Interaction,
                         message:str,
                         game:Game):
  data = None
  errors = []
  if game.Name == 'MAGIC':
    if data is None:
      data, errors = CompanionStandings(message, "    ")
        
    if data is None:
      data, errors = CompanionStandings(message, "\t")
    
    if data is None:
      data, errors = CompanionPairings(message)

  '''
  if game is not None and game.Name == 'Lorcana':
    #Cannot determine what round this is
    if data is None:
      data = LorcanaOfficialPairing(message)
    if data is None:
      data = LorcanaOfficialStanding(message)
  '''
  return data, errors
