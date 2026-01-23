from typing import List
from services.date_functions import ConvertToDate
import discord
from output_builder import BuildTableOutput
from custom_errors import KnownError
from data.add_results_data import AddResult, SubmitTable
from services.input_services import ConvertInput
from data.event_data import GetEvent, CreateEvent, DeleteStandingsFromEvent
from interaction_objects import GetObjectsFromInteraction
from tuple_conversions import Data, Standing, Pairing, Event, Store, Game, Format

def SubmitCheck(interaction:discord.Interaction) -> tuple[Store | None, Game | None, Format | None]:
  """Checks if the user can submit data in this channel"""
  return GetObjectsFromInteraction(interaction)

def SubmitData(store:Store, game:Game, format:Format, userId:int,
               data: list[Standing] | list[Pairing],
               date_str:str,
               round_number:str,
               is_complete: bool,
               whole_event: bool):
  """Submits an event's data to the database"""
  date = ConvertToDate(date_str)
  round_num = int(round_number) if round_number != '' else 0
  
  event = GetEvent(store.DiscordId, date, game, format)
  event_created = False
  if event is None:
    event = CreateEvent(date, store.DiscordId, game, format)
    if event is None:
      raise KnownError('Unable to create event')
    event_created = True

  #Add the data to the database depending on the type of data
  results = ''
  if isinstance(data[0], Standing):
    if event.EventType == 'PAIRINGS' or type(event) is list[Pairing]:
      raise KnownError('This event already has pairings submitted')
    results = AddStandingResults(event, data, userId)
  elif isinstance(data[0], Pairing):
    if event.EventType == 'STANDINGS':
      #Delete the standings data
      DeleteStandingsFromEvent(event.ID)
    results = AddPairingResults(event, data, userId, round_num, whole_event)
  else:
    raise Exception("Congratulations, you've reached the impossible to reach area.")
  return results, event.EventDate if event_created else None

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
      output = AddResult(event.ID, person, submitterId)
      if output:
        successes.append(person)

  title = f'{event.EventDate.strftime("%B %d")} event'
  headers = ['Player Name', 'Wins', 'Losses', 'Draws']
  output = BuildTableOutput(title, headers, successes)
  return output

def AddPairingResults(event:Event,
                      data:list[Pairing],
                      submitterId:int,
                      round_number:int,
                      whole_event:bool):
  round_number = data[0].Round if not round_number else round_number
  successes = []
 
  for table in data:
    result = SubmitTable(event.ID,
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

  if len(successes) > 0:
    title = f"{event.EventDate.strftime('%B %d')} event - Round {round_number}"
    headers = ['Player 1', 'P1 Wins', 'Player 2', 'P2 Wins', 'Result']
    output = BuildTableOutput(title, headers, successes)
    return output
  else:
    return "Sorry, no pairings were added. Please try again later."