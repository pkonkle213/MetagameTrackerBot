from services.date_functions import ConvertToDate
from output_builder import BuildTableOutput
from custom_errors import KnownError
from data.add_results_data import AddResult, SubmitTable
from services.input_services import ConvertInput
from data.event_data import GetEvent, CreateEvent, DeleteStandingsFromEvent
from tuple_conversions import EventInput, Standing, Pairing, Event

def SubmitData(
  submitted_event:EventInput,
  userId:int
): #TODO: What does this return?
  """Submits an event's data to the database"""
  date = ConvertToDate(submitted_event.Date)

  event_created = False
  if submitted_event.ID == 0:
    event_id = CreateEvent(date,
                           submitted_event.StoreID,
                           submitted_event.GameID, 
                           submitted_event.FormatID,
                           submitted_event.Name,
                           submitted_event.TypeID,
                           userId)
    if event_id is None:
      raise KnownError('Unable to create event')
    event_created = True
  else:
    event_id = submitted_event.ID

  event = GetEvent(event_id)

  #Add the data to the database depending on the type of data
  results = ''
  if submitted_event.StandingData:
    if event.reported_as == 'PAIRINGS' or type(event) is list[Pairing]:
      raise KnownError('This event already has pairings submitted')
    results = AddStandingResults(event, submitted_event.StandingData, userId)
  elif submitted_event.PairingData:
    if event.reported_as == 'STANDINGS':
      #Delete the standings data
      DeleteStandingsFromEvent(event.id)
    results = AddPairingResults(event, submitted_event.PairingData, userId, submitted_event.RoundNumber)
  else:
    raise Exception("Congratulations, you've reached the impossible to reach area.")
  return results, event.event_date if event_created else None

def AddStandingResults(event:Event,
                       data:list[Standing],
                       submitterId:int) -> str:
  successes = []
  for person in data:
    if person.PlayerName != '':
      person = Standing(ConvertInput(person.PlayerName),
                        person.Wins,
                        person.Losses,
                        person.Draws)
      output = AddResult(event.id, person, submitterId)
      if output:
        successes.append(person)

  title = f'{event.event_date.strftime("%B %d")} event'
  headers = ['Player Name', 'Wins', 'Losses', 'Draws']
  output = BuildTableOutput(title, headers, successes)
  return output

def AddPairingResults(event:Event,
                      data:list[Pairing],
                      submitterId:int,
                      round_number:int):
  round_number = data[0].Round if not round_number else round_number
  successes = []
 
  for table in data:
    result = SubmitTable(event.id,
                         ConvertInput(table.P1Name),
                         table.P1Wins,
                         ConvertInput(table.P2Name),
                         table.P2Wins,
                         round_number,
                         submitterId)
    
    if result:
      successes.append((ConvertInput(table.P1Name),
                       table.P1Wins,
                       ConvertInput(table.P2Name),
                       table.P2Wins,
                       "Win" if table.P1Wins > table.P2Wins else "Loss" if table.P1Wins < table.P2Wins else "Draw"))

  #TODO: melee.gg data needs to have the round numbers in the table, not the header, as it's a complete event upload
  if len(successes) > 0: 
    title = f"{event.event_date.strftime('%B %d')} - {event.event_name} - Round {round_number}"
    headers = ['Player 1', 'P1 Wins', 'Player 2', 'P2 Wins', 'Result']
    output = BuildTableOutput(title, headers, successes)
    return output
  else:
    return "Sorry, no pairings were added. Please try again later."