import asyncio
import gzip
import json
import math
import re
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

from custom_errors import KnownError
from data.inventory_data import DeductInventory, GetInventoryForNames
from services.object_storage_service import (
    download_file,
    get_object_updated,
    upload_file,
)

SCRYFALL_BULK_URL = (
    "https://api.scryfall.com/bulk-data/"
    "922288cb-4bef-45e1-bb30-0c2bd3d3534f"
)
CARDSPHERE_PRICING_URL = "https://www.cardsphere.com/rest/v2/bulk-data/pricing"
REFERENCE_PREFIX = "Inventory Files/Reference/"
SCRYFALL_FILE = REFERENCE_PREFIX + "all-cards.jsonl.gz"
PRICING_FILE = REFERENCE_PREFIX + "cardsphere-pricing.jsonl"


def ParseTradeInput(text: str) -> list[tuple[int, str]]:
    parsed: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        match = re.fullmatch(r"(\d+)\s*(?:x\s+|-\s+|\s+)(.+?)\s*", line, re.IGNORECASE)
        if not match:
            raise KnownError(
                f"Invalid trade line {line_number}: use “2 Card Name”, “2x Card Name”, or “2 - Card Name”."
            )
        quantity = int(match.group(1))
        name = match.group(2).strip()
        if quantity < 1 or not name:
            raise KnownError(f"Trade line {line_number} needs a positive quantity and card name.")
        parsed.append((quantity, name))
    if not parsed:
        raise KnownError("Enter at least one card to trade.")
    return parsed


def _DownloadToPath(url: str, destination: Path) -> None:
    headers = {"User-Agent": "MetaTracker inventory trade/1.0"}
    with requests.get(url, headers=headers, stream=True, timeout=(20, 600)) as response:
        response.raise_for_status()
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)


def _EnsureCachedFile(
    object_name: str,
    ttl: timedelta,
    path: Path,
    get_download_url,
) -> Path:
    updated = get_object_updated(object_name)
    is_fresh = (
        updated is not None
        and datetime.now(timezone.utc) - updated <= ttl
    )
    if is_fresh:
        download_file(object_name, str(path))
        return path

    url = get_download_url()
    _DownloadToPath(url, path)
    upload_file(str(path), object_name)
    return path


def _GetScryfallDownloadURL() -> str:
    response = requests.get(
        SCRYFALL_BULK_URL,
        headers={"User-Agent": "MetaTracker inventory trade/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["download_uri"]


def _GetCardsphereDownloadURL() -> str:
    response = requests.get(CARDSPHERE_PRICING_URL, timeout=30)
    response.raise_for_status()
    url = response.json().get("url")
    if not url:
        raise KnownError("Cardsphere did not provide a pricing download URL.")
    return url


def _LoadScryfallPrintings(
    path: Path, requested: set[tuple[str, str]]
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    matches: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    requested_editions: dict[str, set[str]] = defaultdict(set)
    for name, edition in requested:
        requested_editions[name].add(edition)
    with gzip.open(path, "rt", encoding="utf-8") as source:
        for line in source:
            card = json.loads(line)
            if card.get("lang") != "en":
                continue
            key_name = str(card.get("name", "")).casefold()
            key_set = str(card.get("set", "")).casefold()
            key_set_name = str(card.get("set_name", "")).casefold()
            for edition in requested_editions.get(key_name, ()):
                if edition in (key_set, key_set_name):
                    matches[(key_name, edition)].append(card)
    return matches


def _LoadNormalPrices(path: Path) -> dict[str, int]:
    prices: dict[str, int] = {}
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            # Inventory does not track finish, so use Cardsphere's non-foil price.
            if record.get("finish") == "N":
                prices[str(record["scryfall_id"])] = int(record["price"])
    return prices


def _Money(cents: int) -> str:
    return f"${cents // 100:,}.{cents % 100:02d}"


def BuildTradeTable(rows: list[tuple[str, int, int, int, int]]) -> tuple[list[str], int]:
    """Format (name, quantity, Cardsphere cents, rounded unit cents, line total cents)."""
    grand_total = sum(row[4] for row in rows)
    grand_total = math.ceil(grand_total / 500) * 500
    headers = ("Card", "Qty", "Cardsphere", "My price", "Total")
    values = [
        (name, str(quantity), _Money(card_price), _Money(my_price), _Money(total))
        for name, quantity, card_price, my_price, total in rows
    ]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in values)) + 2
        for i in range(len(headers))
    ]

    def format_row(row: tuple[str, ...]) -> str:
        return "".join(value.ljust(widths[i]) for i, value in enumerate(row)).rstrip()

    table_rows = [format_row(headers), "-" * sum(widths)]
    table_rows.extend(format_row(row) for row in values)
    table_rows.append(
        format_row(("GRAND TOTAL", "", "", "", _Money(grand_total)))
    )
    body = "\n".join(table_rows)
    chunks: list[str] = []
    while body:
        portion = body[:1900]
        newline = portion.rfind("\n")
        if newline > 0 and newline < len(body):
            portion = body[:newline]
        chunks.append(f"```text\n{portion}\n```")
        body = body[len(portion):].lstrip("\n")
    return chunks, grand_total


async def BuildTrade(text: str) -> list[str]:
    requests_for_trade = ParseTradeInput(text)
    totals: dict[str, int] = defaultdict(int)
    display_names: dict[str, str] = {}
    for quantity, name in requests_for_trade:
        key = name.casefold()
        totals[key] += quantity
        display_names.setdefault(key, name)

    inventory = await GetInventoryForNames(list(display_names.values()))
    by_name: dict[str, list[tuple[int, str, str, int]]] = defaultdict(list)
    for row in inventory:
        by_name[row[1].casefold()].append(row)

    allocations: list[tuple[int, str, str, int]] = []
    for name_key, requested_quantity in totals.items():
        remaining = min(
            requested_quantity,
            sum(row[3] for row in by_name.get(name_key, [])),
        )
        for inventory_id, card_name, edition, available in by_name.get(name_key, []):
            used = min(remaining, available)
            if used:
                allocations.append((inventory_id, card_name, edition, used))
                remaining -= used

    if not allocations:
        raise KnownError("None of the requested cards are currently in inventory.")

    requested_printings = {
        (card_name.casefold(), edition.casefold())
        for _, card_name, edition, _ in allocations
    }

    with tempfile.TemporaryDirectory(prefix="inventory-trade-") as temporary:
        directory = Path(temporary)

        def prepare_references():
            all_cards_path = _EnsureCachedFile(
                SCRYFALL_FILE,
                timedelta(days=30),
                directory / "all-cards.jsonl.gz",
                _GetScryfallDownloadURL,
            )
            pricing_path = _EnsureCachedFile(
                PRICING_FILE,
                timedelta(days=1),
                directory / "cardsphere-pricing.jsonl",
                _GetCardsphereDownloadURL,
            )
            return (
                _LoadScryfallPrintings(all_cards_path, requested_printings),
                _LoadNormalPrices(pricing_path),
            )

        scryfall_cards, prices = await asyncio.to_thread(prepare_references)

    report_rows: list[tuple[str, int, int, int, int]] = []
    deductions: list[tuple[int, int]] = []
    for inventory_id, card_name, edition, quantity in allocations:
        matching = scryfall_cards.get((card_name.casefold(), edition.casefold()), [])
        if not matching:
            raise KnownError(
                f"Could not match {card_name} in edition {edition} in the Scryfall all-cards file."
            )
        collector_numbers = {str(card.get("collector_number", "")) for card in matching}
        if len(collector_numbers) > 1:
            raise KnownError(
                f"{card_name} in {edition} has multiple collector numbers; inventory needs a more specific edition entry."
            )
        card = matching[0]
        card_price = prices.get(str(card.get("id", "")))
        if card_price is None:
            raise KnownError(f"No non-foil Cardsphere price found for {card_name} ({edition}).")
        my_price = math.ceil(card_price / 25) * 25
        line_total = my_price * quantity
        report_rows.append(
            (f"{card_name} ({edition})", quantity, card_price, my_price, line_total)
        )
        deductions.append((inventory_id, quantity))

    messages, _ = BuildTradeTable(report_rows)
    # The deduction locks the table and checks each row ID and available quantity.
    await DeductInventory(deductions)
    return messages
