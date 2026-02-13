from typing import Tuple
from discord.ext import commands
from discord_messages import MessageChannel
from incoming_message_conversions.melee import MeleeJsonPairings
from discord import Guild, Interaction, Attachment
from input_modals.submit_data_modal import SubmitDataModal
from tuple_conversions import Event, Store, Format, Game, Pairing, Standing
from data_translation import ConvertCSVToData, ConvertMessageToData
from datetime import datetime
from custom_errors import KnownError
from services.object_storage_service import upload_bytes, upload_json, upload_string
import pandas as pd
import pytz
import io
import settings

def BuildFilePath(
  store: Store,
  prev_filename: str = ''
) -> str:
  timezone = pytz.timezone('US/Eastern')
  timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
  file_name = f"{timestamp}_{prev_filename}"

  name = store.StoreName if store.StoreName else store.DiscordName
  save_path = f"{store.DiscordId} - {name}/{file_name}"

  return save_path

def ConvertMeleeTournamentToDataErrors(
  store: Store,
  json_data: list
) -> tuple[list[Pairing] | list[Standing], list[str], int, str]:
  path = BuildFilePath(store, 'MeleeTournament.json')
  upload_json(json_data, path)

  data, errors, round_number, date, archetypes = MeleeJsonPairings(json_data)

  #TODO: Do something with archetypes
  return data, errors, round_number, date


async def ConvertCSVToDataErrors(
  bot: commands.Bot,
  store: Store,
  game: Game,
  interaction: Interaction,
  csv_file: Attachment
) -> Tuple[list[Standing]|list[Pairing], list[str] | None, int, str]:
  save_path = BuildFilePath(store, csv_file.filename)
  print('Save path: ', save_path)
  csv_data = await csv_file.read()
  upload_bytes(csv_data, save_path)

  df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')),
                   na_values=['FALSE', 'False'])
  if df is None or df.empty:
    raise KnownError("The file is empty or unreadable. Please try again.")

  data, errors = ConvertCSVToData(df, game)

  filename_split = csv_file.filename.split('-')
  if filename_split[0].upper() == 'STANDINGS':
    round_number = 0
  else:
    round_number = int(filename_split[4])

  date = datetime.now(pytz.timezone('US/Eastern')).strftime("%m/%d/%Y")
  return data, errors, round_number, date


async def ConvertModalToDataErrors(
  bot: commands.Bot,
  interaction: Interaction                                  ,
  store:Store,
  game:Game,
  format:Format,
) -> Tuple[list[Pairing] | list[Standing], list[str], int, str, int]:
  if store is None or game is None or format is None:
    raise KnownError("The princess isn't in this castle.")
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
      'Type: Weekly' if selected_event.TypeID == '1' else 'Type: Monthly'
      f'Message:\n{selected_event.Data}'
    ]
  )

  save_path = BuildFilePath(store, 'ModalInput.txt')
  upload_string(submission, save_path)
  try:
    message = f'Attempting to add new event data from {store.StoreName if store.StoreName else store.DiscordName}:\n{selected_event.Data}'
    await MessageChannel(bot, message, settings.BOTGUILDID,
                       settings.BOTEVENTINPUTID)
  except Exception as e:
    print('Error sending message to channel:', e)

  data, errors, round_number = ConvertMessageToData(selected_event.Data, game)
  date = selected_event.Date
  return data, errors, round_number, date, selected_event.ID