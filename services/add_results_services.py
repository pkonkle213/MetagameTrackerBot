from custom_errors import KnownError
from data.add_results_data import AddResult, SubmitTable
from services.input_services import ConvertInput
from services.date_functions import ConvertToDate
from data.event_data import GetEventObj, CreateEvent
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
  event_created = False
  if event_obj is None:
    event_obj = CreateEvent(date, store.DiscordId, game, format)
    event_created = True
  event = ConvertToEvent(event_obj)
  message = ''
  if isinstance(data[0],Participant):
    message = AddParticipantResults(event, data, userId)
  elif isinstance(data[0], Round):
    message = AddRoundResults(event, data, userId)
  else:
    raise Exception("Congratulations, you've reached the impossible to reach area.")
  return (message, event.EventDate if event_created else None)

def AddParticipantResults(event, data, submitterId):
  successes = 0
  for person in data:
    if person.PlayerName != '':
      person = Participant(ConvertInput(person.PlayerName),
                              person.Wins,
                              person.Losses,
                              person.Draws)
      output = AddResult(event.ID, person, submitterId)
      if output:
        successes += 1

  return f"{successes} entries were added for {event.EventDate.strftime('%B %d')}'s event. {len(data)-successes} were skipped."

def AddRoundResults(event, data, submitterId):
  successes = 0
  round_number = data[0].Round
  for table in data:
    result = SubmitTable(event.ID,
                         ConvertInput(table.P1Name),
                         table.P1Wins,
                         ConvertInput(table.P2Name),
                         table.P2Wins,
                         table.Round,
                         submitterId)
    
    if result:
      successes += 1

  if successes >= 1:
    return f"Ready for the next round, as {successes} entries were added for round {round_number} of {event.EventDate.strftime('%B %d')}'s event."
  else:
    return "Sorry, no entries were added. Please try again later."