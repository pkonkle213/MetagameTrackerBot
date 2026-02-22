from discord.ext import commands
from discord_messages import MessageChannel
from incoming_message_conversions.melee import MeleeJsonPairings
from discord import Interaction, Attachment
from input_modals.submit_data_modal import SubmitDataModal
from services.date_functions import GetToday
from tuple_conversions import EventInput, Store, Format, Game
from data_translation import ConvertCSVToData, ConvertMessageToData
from datetime import datetime
from custom_errors import KnownError
from services.object_storage_service import upload_bytes, upload_json, upload_string
import pandas as pd
import pytz
import io
import settings

#TODO: This needs to know the game and format to be able to save the file in the correct location
def BuildFilePath(
  store: Store,
  game: Game,
  format: Format,
  prev_filename: str = ''
) -> str:
  timezone = pytz.timezone('US/Eastern')
  timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
  file_name = f"{timestamp}_{prev_filename}"
  
  store_name = store.StoreName if store.StoreName else store.DiscordName
  store_folder = f"{store.DiscordId} - {store_name}"
  
  game_name = game.GameName
  format_name = format.FormatName
  today = GetToday()
  year = str(today.year)
  month = str(today.month)
  day = str(today.day)
  
  save_path = "/".join([store_folder, game_name, format_name, year, month, day, file_name])
  print('Save path: ', save_path)

  return save_path

def ConvertMeleeTournamentToDataErrors(
  store: Store,
  game: Game,
  format: Format,
  melee_tournament_id: str,
  event_id: int,
  event_name: str,
  event_type_id: int,
  json_data: list
) -> EventInput:
  path = BuildFilePath(store, game, format, 'MeleeTournament.json')
  upload_json(json_data, path)

  data, errors, round_number, date, archetypes = MeleeJsonPairings(json_data)

  event = EventInput(
    event_id,
    int(melee_tournament_id),
    date,
    event_name,
    event_type_id,
    round_number,
    data,
    None,
    archetypes,
    errors,
    store.DiscordId,
    game.GameId,
    format.FormatId
  )
  return event

async def ConvertCSVToDataErrors(
  bot: commands.Bot,
  store: Store,
  game: Game,
  date: str,
  format: Format,
  interaction: Interaction,
  event_id: int,
  event_name: str,
  event_type_id: int,
  csv_file: Attachment
) -> EventInput:
  save_path = BuildFilePath(store, game, format,  csv_file.filename)
  print('Save path: ', save_path)
  csv_data = await csv_file.read()
  upload_bytes(csv_data, save_path)

  df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')),
                   na_values=['FALSE', 'False'])
  if df is None or df.empty:
    raise KnownError("The file is empty or unreadable. Please try again.")

  standings_data, pairings_data, errors = ConvertCSVToData(df, game)

  filename_split = csv_file.filename.split('-')
  if filename_split[0].upper() == 'STANDINGS':
    round_number = 0
  else:
    round_number = int(filename_split[4])

  custom_event_id = int(filename_split[2])
  
  event = EventInput(
    event_id,
    custom_event_id,
    date,
    event_name,
    event_type_id,
    round_number,
    pairings_data,
    standings_data,
    None,
    errors,
    store.DiscordId,
    game.GameId,
    format.FormatId
  )
  
  return event

async def ConfirmEventDetails(
  bot: commands.Bot,
  interaction: Interaction,
  store:Store,
  game:Game,
  format:Format
) -> tuple[str, str, int, int]:
  modal = SubmitDataModal(store, game, format, False)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError("SubmitData modal was dismissed or timed out. Please try again.")

  selected_event = modal.submitted_event

  return selected_event.Date, selected_event.Name, int(selected_event.ID), int(selected_event.TypeID)

async def ConvertModalToDataErrors(
  bot: commands.Bot,
  interaction: Interaction,
  store:Store,
  game:Game,
  format:Format,
) -> EventInput:
  modal = SubmitDataModal(store, game, format)
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError("SubmitData modal was dismissed or timed out. Please try again.")

  selected_event = modal.submitted_event
  submission = '\n'.join(
    [
      f'Date: {selected_event.Date}',
      f'Name: {selected_event.Name}',
      'Type: Weekly' if selected_event.TypeID == '1' else 'Type: Tournament'
      f'Message:\n{selected_event.Data}'
    ]
  )

  save_path = BuildFilePath(store, game, format, 'ModalInput.txt')
  upload_string(submission, save_path)
  try:
    message = f'Attempting to add new event data from {store.StoreName if store.StoreName else store.DiscordName}:\n{selected_event.Data}'
    await MessageChannel(
      bot,
      message, 
      settings.BOTGUILDID,
      settings.BOTEVENTINPUTID
    )
  except Exception as e:
    print('Error sending message to channel:', e)

  standings_data, pairings_data, errors, round_number = ConvertMessageToData(selected_event.Data, game)
  event = EventInput(
    selected_event.ID,
    None,
    selected_event.Date,
    selected_event.Name,
    int(selected_event.TypeID),
    round_number,
    pairings_data,
    standings_data,
    None,
    errors,
    store.DiscordId,
    game.GameId,
    format.FormatId
  )
  return event