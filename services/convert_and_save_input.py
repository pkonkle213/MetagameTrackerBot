from interaction_objects import GetObjectsFromInteraction
from discord.ext import commands
from discord_messages import MessageChannel
from incoming_message_conversions.melee import MeleeJsonPairings
from discord import Guild, Interaction, Attachment
from input_modals.submit_data_modal import SubmitDataModal
from tuple_conversions import Game, Pairing, Standing
from data_translation import ConvertCSVToData, ConvertMessageToData
from datetime import datetime
from custom_errors import KnownError
from services.object_storage_service import upload_bytes, upload_json, upload_string
import pandas as pd
import pytz
import io
import settings


def BuildFilePath(guild: Guild, prev_filename: str = ''):
  timezone = pytz.timezone('US/Eastern')
  timestamp = datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
  file_name = f"{timestamp}_{prev_filename}"

  save_path = f"{guild.id} - {guild.name}/{file_name}"

  return save_path


def ConvertMeleeTournamentToDataErrors(
    guild: Guild, json_data: list
) -> tuple[list[Pairing] | list[Standing], list[str], str, str]:
  path = BuildFilePath(guild, 'MeleeTournament.json')
  upload_json(json_data, path)

  data, errors, round_number, date, archetypes = MeleeJsonPairings(json_data)

  #TODO: Do something with archetypes
  return data, errors, round_number, date


async def ConvertCSVToDataErrors(bot: commands.Bot, game: Game,
                                 interaction: Interaction,
                                 csv_file: Attachment):
  save_path = BuildFilePath(interaction.guild, csv_file.filename)
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
    round_number = '0'
  else:  #if filename_split[0].upper() == 'MATCHES'
    round_number = filename_split[4]

  date = datetime.now(pytz.timezone('US/Eastern')).strftime("%m/%d/%Y")
  return data, errors, round_number, date


async def ConvertModalToDataErrors(bot: commands.Bot,
                                   interaction: Interaction):
  #Get the data from the user - send modal FIRST before any database operations
  modal = SubmitDataModal()
  await interaction.response.send_modal(modal)
  await modal.wait()

  if not modal.is_submitted:
    raise KnownError(
        "SubmitData modal was dismissed or timed out. Please try again.")

  # Now that modal is submitted, get interaction objects (database operations)
  store, game, format = GetObjectsFromInteraction(interaction)

  submission = '\n'.join([
      f'Date:{modal.submitted_date}', f'Round:{modal.submitted_round}',
      f'Message:\n{modal.submitted_message}'
  ])

  save_path = BuildFilePath(interaction.guild, 'ModalInput.txt')
  upload_string(submission, save_path)
  await MessageChannel(
      bot,
      f'Attempting to add new event data from {store.StoreName}:\n{modal.submitted_message}',
      settings.BOTGUILDID, settings.BOTEVENTINPUTID)

  #Convert the data to the appropriate format
  data, errors = ConvertMessageToData(modal.submitted_message, game)
  round_number = modal.submitted_round
  date = modal.submitted_date
  return data, errors, round_number, date, store, game, format
