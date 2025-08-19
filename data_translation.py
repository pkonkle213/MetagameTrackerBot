from discord import Interaction
from incoming_message_conversions.magic_companion import CompanionParticipants, CompanionRoundByRound, CompanionParticipantsWithTabs
from incoming_message_conversions.lorcana_official import LorcanaOfficialRound, LorcanaOfficialParticipant
from interaction_data import GetInteractionData

def ConvertMessageToData(interaction:Interaction, message:str):
  game = GetInteractionData(interaction, game=True).Game

  data = None
  errors = []
  if game is not None and game.Name == 'MAGIC':
    if data is None:
      data, errors = CompanionParticipants(message)
        
    if data is None:
      data, errors = CompanionParticipantsWithTabs(message)
    
    if data is None:
      data, errors = CompanionRoundByRound(message)

  '''
  if game is not None and game.Name == 'Lorcana':
    #Cannot determine what round this is
    if data is None:
      data = LorcanaOfficialRound(message)
    if data is None:
      data = LorcanaOfficialParticipant(message)
  '''
  return data, game, errors


"""
  if data is None:
    data = MeleeParticipants(message)
    
def MeleeParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 3):
      name = ' '.join(rows[i + 1].split(' ')[0:-1])
      record = rows[i + 2].split('    ')[0].split('-')
      participant = Participant(name,
                                int(record[0]),
                                int(record[1]),
                                int(record[2]))
      data.append(participant)
    return data
  except Exception as exception:
    print('Rows:', rows)
    print('Melee Participants Exception:', exception)
    return None
"""

'''
TODO: League data
I would like to receive data meant for leagues and digest it into the database
What I need to be reported is the match number, the players' names, the players' archetype, and each player's game win count
ObjReceived(match_number, player1_name, player1_archetype, player1_game_wins, player2_name, player2_archetype, player2_game_wins)
Most likely this will need to go into the rounds table and the archetype table
Issue is though, how do I link the correct archetype to the correct player and the correct match, because archetypes are currently linked to event_id and player_name.
I may need to add a new table and condense the data into another view
'''