from enum import Enum, auto
from custom_errors import KnownError
from database_connection import GetEventObj, CreateEvent, AddResult, GetRoundNumber, GetParticipantId, Increase, AddRoundResult, SubmitTable
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
  print('Event Obj:', event_obj)
  if event_obj is None:
    event_obj = CreateEvent(date, store.DiscordId, game, format)

  print('Event Obj2:', event_obj)

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

def AddRoundResults(event, data, submitterId):
  successes = 0
  round_number = GetRoundNumber(event.ID) + 1
  for table in data:
    result = SubmitTable(event.ID,
                         table.P1Name.upper(),
                         table.P1Wins,
                         table.P2Name.upper(),
                         table.P2Wins,
                         round_number,
                         submitterId)
    
    if result:
      successes += 1

  if successes >= 1:
    return f"Ready for the next round, as {successes} entries were added for round {round_number} of {event.EventDate.strftime('%B %d')}'s event. Feel free to use /claim and update the archetypes!"
  else:
    return "Sorry, no entries were added. Please try again later."