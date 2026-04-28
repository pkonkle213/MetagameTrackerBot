from api_calls.melee_tournaments import GetMeleeTournamentData
from discord.ext import commands
from discord_messages import MessageChannel
from incoming_message_conversions.melee import MeleeJsonPairings
from discord import Interaction, Attachment
from services.date_functions import GetToday
from tuple_conversions import EventInput, Store, Format, Game, Pairing, Standing, Event, Archetype, DataConverted
from data_translation import ConvertCSVToData, ConvertMessageToData
from datetime import date, datetime
from custom_errors import KnownError
from services.object_storage_service import upload_bytes, upload_json, upload_string
import pandas as pd
import pytz
import io
import settings
from typing import NamedTuple


async def ConvertData(
  event:EventInput,
  data:str | None,
  csv_file:Attachment | None,
  melee_tournament_id:str,
  store:Store,
  game:Game,
  format:Format
) -> DataConverted:
  event_input:DataConverted | None = None
  
  if data:
    event_input = ConvertAndUploadMessage(event, data, store, game, format)
  elif csv_file: #I need to receive a round number for this, as the CSV doesn't have it
    event_input = await ConvertAndUploadCSV(event, csv_file, store, game, format)
  elif melee_tournament_id:
    event_input = ConvertAndUploadMeleeTournament(event, melee_tournament_id, store, game, format)

  if event_input is None:
    raise KnownError("No data was submitted. Please try again.")

  return event_input
  
def BuildFilePath(
  store: Store,
  game: Game,
  format: Format,
  prev_filename: str = ''
) -> str:
  """Builds the file path for the file to be saved in App Storage"""
  timezone = pytz.timezone('US/Eastern')
  timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
  file_name = f"{timestamp}_{prev_filename}"
  
  store_name = store.store_name if store.store_name else store.discord_name
  store_folder = f"{store.discord_id} - {store_name}"
  
  game_name = game.game_name
  format_name = format.format_name
  today = GetToday()
  year = str(today.year)
  month = f"{today.month:02d}"
  day = f"{today.day:02d}"
  
  save_path = "/".join([store_folder, game_name, format_name, year, month, day, file_name])

  return save_path

def ConvertAndUploadMeleeTournament(
  event: EventInput,
  melee_tournament_id: str,
  store: Store,
  game: Game,
  format: Format,
) -> DataConverted:
  """Takes in a Melee.gg tournament id, retrieves the data, and converts the data to a list of Pairing objects"""
  json_data = GetMeleeTournamentData(melee_tournament_id, store)
  
  path = BuildFilePath(store, game, format, 'MeleeTournament.json')
  upload_json(json_data, path)

  data, errors, round_number, date, archetypes = MeleeJsonPairings(json_data)
  return DataConverted(
    data,
    None,
    errors,
    round_number,
    date,
    archetypes,
    event.custom_event_id
  )

async def ConvertAndUploadCSV(
  event: EventInput,
  csv_file: Attachment,
  store: Store,
  game: Game,
  format: Format
) -> DataConverted:
  """Takes in a CSV file and converts it to a list of Pairing or Standing objects"""
  save_path = BuildFilePath(store, game, format, csv_file.filename)
  csv_data = await csv_file.read()
  upload_bytes(csv_data, save_path)

  df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')),
                   na_values=['FALSE', 'False'])
  if df is None or df.empty:
    raise KnownError("The file is empty or unreadable. Please try again.")

  submitted_data = ConvertCSVToData(df)

  filename_split = csv_file.filename.split('-')
  if filename_split[0].upper() == 'STANDINGS':
    round_number = 0
  else:
    round_number = int(filename_split[4])

  custom_event_id = int(filename_split[2])
  
  return DataConverted(
    submitted_data.pairings_data,
    submitted_data.standings_data,
    submitted_data.errors,
    round_number,
    event.event_date,
    None,
    custom_event_id
  )
  
  return event

def ConvertAndUploadMessage(
  event:EventInput,
  data:str,
  store:Store,
  game:Game,
  format:Format
) -> DataConverted:
  match event.event_type_id:
    case 1:
      event_type = 'Weekly'
    case 2:
      event_type = 'Tournament'
    case _:
      event_type = 'League'
      
  submission = '\n'.join(
    [
      f'Date: {event.event_date.strftime('%m/%d/%Y') if event.event_date else ''}',
      f'Name: {event.event_name}',
      f'Type: {event_type}',
      f'Message:\n{data}'
    ]
  )

  save_path = BuildFilePath(store, game, format, 'ModalInput.txt')
  upload_string(submission, save_path)
  
  converted_data = ConvertMessageToData(data, game.id)

  return converted_data
