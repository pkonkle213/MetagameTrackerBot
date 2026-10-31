import asyncio
import csv
import io
import re

from custom_errors import KnownError
from data.inventory_data import ReplaceInventory
from services.object_storage_service import get_latest_file_bytes

INVENTORY_FOLDER = "Inventory Files/"


def _NormalizeHeader(header: str) -> str:
    return re.sub(r"[\s_-]+", " ", header.strip().casefold())


def ParseInventoryCSV(content: bytes) -> list[tuple[int, str, str]]:
    try:
        reader = csv.DictReader(
            io.StringIO(content.decode("utf-8-sig")), restkey="_extra_fields"
        )
        fieldnames = reader.fieldnames
    except (UnicodeDecodeError, csv.Error) as error:
        raise KnownError("The latest inventory file is not a valid UTF-8 CSV.") from error

    if not fieldnames:
        raise KnownError("The inventory CSV must include a header row.")

    aliases = {
        "quantity": {"quantity", "qty"},
        "card name": {"card name", "name"},
        "card edition": {"card edition", "edition", "set"},
    }
    header_map: dict[str, str] = {}
    normalized_headers = [
        (_NormalizeHeader(name), name) for name in fieldnames if name
    ]
    for required, accepted in aliases.items():
        matches = [
            original
            for normalized, original in normalized_headers
            if normalized in accepted
        ]
        if len(matches) != 1:
            raise KnownError(
                "The inventory CSV needs one each of Quantity, Card Name, and Card Edition."
            )
        header_map[required] = matches[0]

    rows: list[tuple[int, str, str]] = []
    try:
        for row in reader:
            if row.get("_extra_fields"):
                raise KnownError(
                    f"CSV row {reader.line_num} has more values than the header."
                )
            if all(
                not (value or "").strip()
                for value in row.values()
                if isinstance(value, str) or value is None
            ):
                continue
            quantity_text = (row.get(header_map["quantity"]) or "").strip()
            card_name = (row.get(header_map["card name"]) or "").strip()
            card_edition = (row.get(header_map["card edition"]) or "").strip()
            try:
                quantity = int(quantity_text)
            except ValueError as error:
                raise KnownError(
                    f"Invalid quantity on CSV row {reader.line_num}: {quantity_text!r}."
                ) from error
            if quantity < 0 or not card_name or not card_edition:
                raise KnownError(
                    f"CSV row {reader.line_num} must have a non-negative quantity, card name, and card edition."
                )
            rows.append((quantity, card_name, card_edition))
    except csv.Error as error:
        raise KnownError("The inventory CSV could not be parsed.") from error

    if not rows:
        raise KnownError("The inventory CSV contains no inventory rows; existing data was not changed.")
    return rows


async def SyncInventoryFromLatestFile() -> tuple[str, int]:
    try:
        file_name, content = await asyncio.to_thread(
            get_latest_file_bytes, INVENTORY_FOLDER, ".csv"
        )
    except FileNotFoundError as error:
        raise KnownError(
            "No CSV file was found in the App Storage folder “Inventory Files”."
        ) from error

    rows = ParseInventoryCSV(content)
    inserted = await ReplaceInventory(rows)
    return file_name, inserted
