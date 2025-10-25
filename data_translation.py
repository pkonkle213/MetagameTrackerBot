from discord import Interaction
from incoming_message_conversions.magic_companion import CompanionStandings, CompanionPairings
from incoming_message_conversions.lorcana_official import LorcanaOfficialPairing, LorcanaOfficialStanding
from incoming_message_conversions.melee import MeleeStandings, MeleePairings
from tuple_conversions import Game

def ConvertMessageToData(interaction:Interaction,
                         message:str,
                         game:Game):
  data = None
  print('Game:', game)
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

  if game.Name.upper() == 'LORCANA':
    print('Attempting to parse Lorcana Official Pairings Data')
    
    if data is None:
      print('Testing Lorcana Official Pairings')
      data = LorcanaOfficialPairing(message)
      
    if data is None:
      print('Testing Lorcana Official Standings')
      data = LorcanaOfficialStanding(message)

  if data is None:
    print('Attempting to parse Melee Standings Data')
    data, errors = MeleeStandings(message)

  if data is None:
    print('Attempting to parse Melee Pairings Data')
    data, errors = MeleePairings(message)

  
  return data, errors
