from datetime import datetime
from typing import Any, NamedTuple

import requests
from custom_errors import KnownError
from data.melee_api_data import GetStoreMeleeInfo
from tuple_conversions import Store


class MeleeTournamentData(NamedTuple):
    pairings: list[Any]
    event_details: dict[str, Any] | None
    event_details_error: str | None = None


async def _GetMeleeCredentials(store: Store) -> tuple[str, str]:
    store_info = await GetStoreMeleeInfo(store)
    if (
        not store_info
        or store_info.melee_client_id is None
        or store_info.melee_client_secret is None
    ):
        raise KnownError(
            "Store not registered for Melee.gg API. Update store settings and try again."
        )
    return store_info.melee_client_id, store_info.melee_client_secret


async def GetMeleeTournamentPairings(tournament_id: str, store: Store) -> list[Any]:
    client_id, client_secret = await _GetMeleeCredentials(store)
    page_size = 250
    has_more = True
    data: list[Any] = []
    page = 1

    while has_more:
        api_url = (
            f"https://melee.gg/api/match/list/{tournament_id}"
            f"?variables.page={page}&variables.pageSize={page_size}"
        )
        try:
            response = requests.get(api_url, auth=(client_id, client_secret))
        except requests.RequestException as error:
            raise KnownError(
                "Unable to get data from Melee.gg. Please try again."
            ) from error

        if response.status_code != 200:
            raise KnownError("Unable to get data from Melee.gg. Please try again.")

        try:
            response_obj = response.json()
            data += response_obj["Content"]
            has_more = response_obj["HasMore"]
        except (ValueError, KeyError, TypeError) as error:
            raise KnownError(
                "Melee.gg returned invalid pairing data. Please try again."
            ) from error
        page += 1

    if not data:
        raise KnownError("No data found for this tournament. Please try again.")
    return data


async def GetMeleeTournamentDetails(
    tournament_id: str, store: Store
) -> dict[str, Any]:
    client_id, client_secret = await _GetMeleeCredentials(store)
    api_url = f"https://melee.gg/api/tournament/{tournament_id}"
    try:
        response = requests.get(api_url, auth=(client_id, client_secret))
    except requests.RequestException as error:
        raise KnownError(
            "Unable to get event details from Melee.gg. Please try again."
        ) from error

    if response.status_code != 200:
        raise KnownError("Unable to get event details from Melee.gg. Please try again.")

    try:
        event_details = response.json()
        if not isinstance(event_details, dict):
            raise TypeError("Event details must be an object")
        name = event_details["Name"]
        last_pair_datetime = event_details["LastPairDateTime"]
        int(event_details["ID"])
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Event name is empty")
        if not isinstance(last_pair_datetime, str):
            raise TypeError("LastPairDateTime must be a string")
        datetime.fromisoformat(last_pair_datetime.replace("Z", "+00:00"))
    except (ValueError, KeyError, TypeError) as error:
        raise KnownError(
            "Melee.gg returned invalid event details. Please try again."
        ) from error

    return event_details


async def GetMeleeTournamentData(
    tournament_id: str, store: Store
) -> MeleeTournamentData:
    pairings = await GetMeleeTournamentPairings(tournament_id, store)
    try:
        event_details = await GetMeleeTournamentDetails(tournament_id, store)
    except KnownError as error:
        # Refresh pairings before asking the user to confirm a replacement.
        pairings = await GetMeleeTournamentPairings(tournament_id, store)
        return MeleeTournamentData(pairings, None, str(error))

    return MeleeTournamentData(pairings, event_details)
