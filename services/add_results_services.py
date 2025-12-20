from datetime import date
from services.date_functions import ConvertToDate
import discord
from custom_errors import KnownError
from data.add_results_data import AddResult, SubmitTable
from services.input_services import ConvertInput
from data.event_data import GetEvent, CreateEvent, DeleteStandingsFromEvent
from interaction_objects import GetObjectsFromInteraction
from models.interactionData import Data
from models.event import Event
from models.pairing import Pairing
from models.standing import Standing


def SubmitCheck(interaction:discord.Interaction) -> Data:
  """Checks if the user can submit data in this channel"""
  return GetObjectsFromInteraction(interaction,
                                   game=True,
                                   format=True,
                                   store=True)

def SubmitData(interaction_objects:Data,
               data: list[Standing] | list[Pairing],
               date_str:str,
               round_number:str,
               whole_event: bool) -> tuple[str, date | None]:
  """Submits an event's data to the database"""
  store = interaction_objects.Store
  game = interaction_objects.Game
  format = interaction_objects.Format
  userId = interaction_objects.UserId

  date = ConvertToDate(date_str)
  round_num = int(round_number) if round_number != '' else 0
  if not store or not game or not format:
    raise KnownError('Insufficient criteria to submit data')
  event = GetEvent(store.DiscordId, date, game, format)
  event_created = False
  if event is None:
    event = CreateEvent(date, store.DiscordId, game, format)
    event_created = True

  #Add the data to the database depending on the type of data
  results = ''
  if any(isinstance(item, Standing) for item in data):
    if event.EventType.upper() == 'PAIRINGS':
      raise KnownError('This event already has pairings submitted')
    results = AddStandingResults(event, data, userId)
  elif any(isinstance(item, Pairing) for item in data):
    if event.EventType == 'STANDINGS':
      #Delete the standings data
      DeleteStandingsFromEvent(event.EventId)
    results = AddPairingResults(event, data, userId, round_num, whole_event)

  return results, event.EventDate if event_created else None

def AddStandingResults(event:Event,
                       data:list[Standing],
                       submitterId:int) -> str:
  successes = 0
  for person in data:
    if person.PlayerName != '':
      name = ConvertInput(person.PlayerName)
      person = Standing(name,
                        person.Wins,
                        person.Losses,
                        person.Draws)
      output = AddResult(event.EventId, person, submitterId)
      if output:
        successes += 1

  result = f"{successes} players were added for {event.EventDate.strftime('%B %d')}'s event."
  if len(data)-successes > 0:
    result += f"{len(data)-successes} were skipped."
  return result

def AddPairingResults(event:Event,
                      data:list[Pairing],
                      submitterId:int,
                      round_number:int,
                      whole_event:bool):
  successes = 0
 
  for table in data:
    round_number = data[0].RoundNumber if not round_number else round_number
    p1name = ConvertInput(table.P1Name)
    p2name = ConvertInput(table.P2Name)
    table = Pairing(p1name,
    table.P1Wins,
    p2name,
    table.P2Wins,
    round_number)
    result = SubmitTable(event.EventId,
                         table,                         
                         submitterId)
    
    if result:
      successes += 1

  if successes >= 1:
    if whole_event:
      return f"{successes} entries were pairings for {event.EventDate.strftime('%B %-d')}'s event."
    return f"Ready for the next round, as {successes} pairings were added for round {round_number} of {event.EventDate.strftime('%B %-d')}'s event."
  else:
    return "Sorry, no pairings were added. Please try again later."