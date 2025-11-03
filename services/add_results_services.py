from services.date_functions import ConvertToDate
from typing import List
import discord
from custom_errors import KnownError
from data.add_results_data import AddResult, SubmitTable
from services.input_services import ConvertInput
from data.event_data import GetEvent, CreateEvent, DeleteStandingsFromEvent
from interaction_objects import GetObjectsFromInteraction
from tuple_conversions import Data, Standing, Pairing, Event

def SubmitCheck(interaction:discord.Interaction):
  """Checks if the user can submit data in this channel"""
  return GetObjectsFromInteraction(interaction,
                                   game=True,
                                   format=True,
                                   store=True)

def SubmitData(interaction_objects:Data,
               data: List[Standing] | List[Pairing],
               date_str:str,
               round_number:str,
               is_complete: bool):
  """Submits an events data to the database"""
  store = interaction_objects.Store
  game = interaction_objects.Game
  format = interaction_objects.Format
  userId = interaction_objects.UserId

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
  #TODO: is_complete needs to be added to the database
  results = ''
  if isinstance(data[0], Standing):
    if event.EventType != 'STANDINGS':
      raise KnownError('This event already has pairings submitted')
    results = AddStandingResults(event, data, userId)
  elif isinstance(data[0], Pairing):
    if event.EventType != 'PAIRINGS':
      #Delete the standings data
      DeleteStandingsFromEvent(event.ID)
    results = AddPairingResults(event, data, userId, round_num)
  else:
    raise Exception("Congratulations, you've reached the impossible to reach area.")
  return results, event.EventDate if event_created else None

def AddStandingResults(event:Event,
                       data:List[Standing],
                       submitterId:int):
  successes = 0
  for person in data:
    if person.PlayerName != '':
      person = Standing(ConvertInput(person.PlayerName),
                              person.Wins,
                              person.Losses,
                              person.Draws)
      output = AddResult(event.ID, person, submitterId)
      if output:
        successes += 1

  output = f"{successes} entries were added for {event.EventDate.strftime('%B %d')}'s event."
  if len(data)-successes > 0:
    output += f"{len(data)-successes} were skipped."
  return 

def AddPairingResults(event:Event,
                      data:List[Pairing],
                      submitterId:int,
                      round_number:int):
  round_number = data[0].Round if not round_number else round_number
  successes = 0
 
  for table in data:
    result = SubmitTable(event.ID,
                         ConvertInput(table.P1Name),
                         table.P1Wins,
                         ConvertInput(table.P2Name),
                         table.P2Wins,
                         round_number,
                         submitterId)
    
    if result:
      successes += 1

  #TODO: The day should not have a leading zero
  if successes >= 1:
    return f"Ready for the next round, as {successes} entries were added for round {round_number} of {event.EventDate.strftime('%B %d')}'s event."
  else:
    return "Sorry, no entries were added. Please try again later."