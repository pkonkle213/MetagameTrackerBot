from enum import Enum, auto
from database_connection import GetEventObj, CreateEvent, AddResult
from date_functions import GetToday
from interaction_data import GetInteractionData
from tuple_conversions import ConvertToEvent

async def SubmitData(bot, message, data):
  game, format, store, userId = GetInteractionData(message,
                                                   game=True,
                                                   format=True,
                                                   store=True)
  #TODO: Should I Confirm date? How do I handle data that's input late?
  event_date = GetToday()
  event_obj = GetEventObj(store.DiscordId, event_date, game, format)
  
  if event_obj is None:
    event_obj = CreateEvent(event_date, store.DiscordId, game, format)

  event = ConvertToEvent(event_obj)
  output = AddParticipantResults(event.ID, data, userId)
  return output

def AddParticipantResults(event_id, data, submitterId):
  successes = 0
  for person in data:
    output = AddResult(event_id, person, submitterId)
    if output:
      successes += 1

  return f'{successes} entries were added. Feel free to use /claim and update the archetypes!'

#####################################################################################################
#TODO: Not implemented, needs to be updated and retweaked
class Winner(Enum):
  TIE = auto()
  PLAYER1 = auto()
  PLAYER2 = auto()

def AddRoundResults(event_id, data, submitterId):
  round_number = (database_connection.GetRoundNumber(event_id) or 0) + 1
  print('Round number:', round_number)
  for round in data:
    result = None
    if round.P1Wins > round.P2Wins:
      result = Winner.PLAYER1
    elif round.P2Wins > round.P1Wins:
      result = Winner.PLAYER2
    else:
      result = Winner.TIE

    player1id = database_connection.GetParticipantId(event_id,
                                                     round.P1Name.upper())
    player2id = database_connection.GetParticipantId(event_id,
                                                     round.P2Name.upper())

    if player1id is None:
      person = tuple_conversions.Participant(round.P1Name.upper(), 0, 0, 0)
      player1id = database_connection.AddResult(event_id, person,
                                                submitterId)

    if player2id is None:
      person = tuple_conversions.Participant(round.P2Name.upper(), 0, 0, 0)
      player2id = database_connection.AddResult(event_id, person,
                                                submitterId)

    #increase each player's wins, losses, and draws by 1 where appropriate
    if result == Winner.PLAYER1:
      database_connection.Increase(player1id, 1, 0, 0)
      database_connection.Increase(player2id, 0, 1, 0)
      database_connection.AddRoundResult(event_id, round_number, player1id,
                                         player2id, player1id)
    elif result == Winner.PLAYER2:
      database_connection.Increase(player2id, 1, 0, 0)
      database_connection.Increase(player1id, 0, 1, 0)
      database_connection.AddRoundResult(event_id, round_number, player1id,
                                         player2id, player2id)
    elif result == Winner.TIE:
      database_connection.Increase(player1id, 0, 0, 1)
      database_connection.Increase(player2id, 0, 0, 1)
      database_connection.AddRoundResult(event_id, round_number, player1id,
                                         player2id, None)