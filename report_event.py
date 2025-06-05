from enum import Enum, auto
from custom_errors import KnownError
from database_connection import GetEventObj, CreateEvent, AddResult, GetRoundNumber, GetParticipantId, Increase, AddRoundResult
from date_functions.date_functions import ConvertToDate
from interaction_data import GetInteractionData
from tuple_conversions import ConvertToEvent, Participant, Round

async def SubmitData(message, data, date_str):
  game, format, store, userId = GetInteractionData(message,
                                                   game=True,
                                                   format=True,
                                                   store=True)
  if store is None or not store.ApprovalStatus:
    raise KnownError('This store is not approved to submit data.')
  
  date = ConvertToDate(date_str)    
  event_obj = GetEventObj(store.DiscordId, date, game, format)
  if event_obj is None:
    event_obj = CreateEvent(date, store.DiscordId, game, format)

  event = ConvertToEvent(event_obj)
  if isinstance(data[0],Participant):
    output = AddParticipantResults(event, data, userId)
  elif isinstance(data[0], Round):
    output = AddRoundResults(event, data, userId)
  else:
    raise Exception("Congratulations, you've reached the impossible to reach area.")
  return output

def AddParticipantResults(event, data, submitterId):
  successes = 0
  for person in data:
    if person.PlayerName != '':
      output = AddResult(event.ID, person, submitterId)
      if output:
        successes += 1

  return f"{successes} entries were added for {event.EventDate.strftime('%B %d')}'s event. {len(data)-successes} were skipped. Feel free to use /claim and update the archetypes!"

class Winner(Enum):
  TIE = auto()
  PLAYER1 = auto()
  PLAYER2 = auto()

def AddRoundResults(event, data, submitterId):
  successes = 0
  round_number = GetRoundNumber(event.ID) + 1
  for round in data:
    if round.P1Wins > round.P2Wins:
      result = Winner.PLAYER1
    elif round.P2Wins > round.P1Wins:
      result = Winner.PLAYER2
    else:
      result = Winner.TIE

    player1id = GetParticipantId(event.ID,
                                 round.P1Name.upper())
    player2id = GetParticipantId(event.ID,
                                 round.P2Name.upper())

    if player1id is None:
      person = Participant(round.P1Name.upper(), 0, 0, 0)
      player1id = AddResult(event.ID,
                            person,
                            submitterId)
  
    if round.P2Name != 'Bye' and player2id is None:
      person = Participant(round.P2Name.upper(), 0, 0, 0)
      player2id = AddResult(event.ID,
                            person,
                            submitterId)
    elif round.P2Name == 'Bye':
      player2id = None

    winner_id = player1id if result == Winner.PLAYER1 else player2id if result == Winner.PLAYER2 else None
    increase_one = Increase(player1id,
                            1 if result == Winner.PLAYER1 else 0,
                            1 if result == Winner.PLAYER2 else 0,
                            1 if result == Winner.TIE else 0)
    if not increase_one:
      raise Exception('Unable to increase participant record one')
    if round.P2Name.lower() != 'bye':
      increase_two = Increase(player2id,
                              1 if result == Winner.PLAYER2 else 0,
                              1 if result == Winner.PLAYER1 else 0,
                              1 if result == Winner.TIE else 0)
      if not increase_two:
        raise Exception('Unable to increase participant record two')
    
    result = AddRoundResult(event.ID,
                            round_number,
                            player1id,
                            player2id,
                            winner_id,
                            submitterId)
    if result:
      successes += 1

  return f"Ready for the next round, as {successes} entries were added for {event.EventDate.strftime('%B %d')}'s event. Feel free to use /claim and update the archetypes!"