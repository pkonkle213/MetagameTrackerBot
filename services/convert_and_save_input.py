from api_calls.melee_tournaments import GetMeleeTournamentData
from incoming_message_conversions.melee import MeleeJsonPairings
from discord import Attachment
from services.date_functions import GetToday
from tuple_conversions import Store, Format, Game, Event, DataConverted
from data_translation import ConvertCSVToData, ConvertMessageToData
from datetime import datetime
from custom_errors import KnownError
from services.object_storage_service import upload_bytes, upload_json, upload_string
import pandas as pd
import pytz
import io


def BuildFilePath(
    store: Store, game: Game, format: Format, prev_filename: str = ""
) -> str:
    """Builds the file path for the file to be saved in App Storage"""
    timezone = pytz.timezone("US/Eastern")
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

    save_path = "/".join(
        [store_folder, game_name, format_name, year, month, day, file_name]
    )

    return save_path


def ConvertAndUploadMeleeTournament(
    event, melee_tournament_id: str, store: Store, file_path: str
) -> DataConverted:
    """Takes in a Melee.gg tournament id, retrieves the data, and converts the data to a list of Pairing objects"""
    json_data = GetMeleeTournamentData(melee_tournament_id, store)

    try:
        upload_json(json_data, file_path)
    except Exception as e:
        print("Tried to save JSON data to App Storage and failed.")

    data, errors, round_number, date, archetypes = MeleeJsonPairings(json_data)
    return DataConverted(data, None, errors, archetypes, event.custom_event_id)


async def ConvertAndUploadCSV(
    event: Event, file_path: str, csv_file: Attachment
) -> DataConverted:
    """Takes in a CSV file and converts it to a list of Pairing or Standing objects"""
    csv_data = await csv_file.read()

    try:
        upload_bytes(csv_data, file_path)
    except Exception as e:
        print("Tried to save CSV data to App Storage and failed.")

    df = pd.read_csv(
        io.StringIO(csv_data.decode("utf-8")), na_values=["FALSE", "False"]
    )
    if df is None or df.empty:
        raise KnownError("The file is empty or unreadable. Please try again.")

    filename_split = csv_file.filename.split("-")
    if filename_split[0].upper() == "STANDINGS":
        round_number = 0
    else:
        round_number = int(filename_split[4])

    submitted_data = ConvertCSVToData(df)

    custom_event_id = int(filename_split[2])

    return DataConverted(
        submitted_data.pairings_data,
        submitted_data.standings_data,
        submitted_data.errors,
        None,
        custom_event_id,
    )

    return event


def ConvertAndUploadMessage(
  event: Event,
  save_path: str,
  data: str
) -> DataConverted:
    match event.event_type_id:
        case 1:
            event_type = "Weekly"
        case 2:
            event_type = "Tournament"
        case _:
            event_type = "League"

    submission = "\n".join(
        [
            f"Date: {event.event_date.strftime('%m/%d/%Y') if event.event_date else ''}",
            f"Name: {event.event_name}",
            f"Type: {event_type}",
            f"Message:\n{data}",
        ]
    )

    try:
        upload_string(submission, save_path)
    except Exception as e:
        print("Tried to save message data to App Storage and failed.")

    converted_data = ConvertMessageToData(data)

    return converted_data
