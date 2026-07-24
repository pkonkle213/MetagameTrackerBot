from typing import Tuple
from output_builder import BuildTableOutput
from custom_errors import KnownError
from data.add_results_data import InsertStanding, InsertPairing, CheckPairings
from services.input_services import ConvertInput
from data.event_data import GetEvent, CreateEvent, DeleteStandingsFromEvent
from tuple_conversions import Standing, Pairing, Event, ReportedAsEnum

def AddStandingResults(
  event:Event,
  data:list[Standing],
  submitterId:int
) -> list[Standing]:
  errors:list[Standing] = []
  for person in data:
    if person.player_name != '':
      person = Standing(ConvertInput(person.player_name),
                        person.wins,
                        person.losses,
                        person.draws)
      output = InsertStanding(event.id, person, submitterId)
      if not output:
        errors.append(person)

  return errors

def AddPairingResults(
  event:Event,
  data:list[Pairing],
  submitterId:int,
  round_number:int
) -> list[Pairing]:
  const_round_number = data[0].round_number if not round_number else round_number
  errors:list[Pairing] = []
  output = ''
 
  for table in data:
    p1name = ConvertInput(table.player1_name)
    p2name = ConvertInput(table.player2_name)
    round_number = table.round_number if table.round_number else const_round_number

    unique = CheckPairings(event.id, round_number, p1name, p2name)
    if unique:
      pairing = Pairing(
        round_number,
        p1name,
        table.player1_game_wins,
        table.player2_game_wins,
        p2name
      )
      
      db_result = InsertPairing(
        event.id,
        pairing,
        submitterId
      )
      
      if not db_result:
        errors.append(pairing)
    else:
      errors.append(pairing)

  return errors
  