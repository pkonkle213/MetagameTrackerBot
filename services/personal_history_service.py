from custom_errors import KnownError
from data.personal_history_data import (
    GetHubPairingsHistory,
    GetHubStandingsHistory,
    GetStorePairingsHistory,
    GetStoreStandingsHistory,
)
from output_builder import BuildTableOutput
from services.date_functions import BuildDateRange
from tuple_conversions import InteractionObjects


async def GetPersonalStandingsHistory(
    user_id: int,
    start_date: str,
    end_date: str,
    objects: InteractionObjects | None,
) -> list[str]:
    """Gets the personal standings history for the user"""
    if not objects or not objects.store and not objects.hub:
        raise KnownError("No store or hub found")

    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
    headers = ["Date", "Archetype", "Wins", "Losses", "Draws"]
    data = []

    if not objects.format:
        headers.insert(1, "Format")
    if not objects.game:
        headers.insert(1, "Game")
    if objects.hub and not objects.region:
        headers.insert(1, "Region")

    if objects.store:
        data = await GetStoreStandingsHistory(
            user_id,
            objects.store,
            objects.game,
            objects.format,
            date_start,
            date_end,
        )
    elif objects.hub:
        data = await GetHubStandingsHistory(
            user_id,
            objects.hub,
            objects.region,
            objects.game,
            objects.format,
            date_start,
            date_end,
        )
        headers.insert(2, "Store Name")

    name = "You"
    if objects.hub:
        name = objects.hub.hub_name
    elif objects.store:
        name = objects.store.store_name

    if len(data) == 0:
        return ["No history found."]

    title = f"Personal History for {name.title()}"

    output = BuildTableOutput(title, headers, data)
    return output


async def GetPersonalPairingsHistory(
    user_id: int,
    start_date: str,
    end_date: str,
    objects: InteractionObjects | None,
) -> list[str]:
    """Gets the personal pairings history for the user"""
    if not objects or (not objects.store and not objects.hub):
        raise KnownError("No store or hub found")

    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
    headers = ["Date", "Round", "Your Archetype", "Opponent's Archetype", "Result"]
    data = []

    if not objects.format:
        headers.insert(1, "Format")
    if not objects.game:
        headers.insert(1, "Game")
    if objects.hub and not objects.region:
        headers.insert(1, "Region")

    if objects.store:
        data = await GetStorePairingsHistory(
            user_id,
            objects.store,
            objects.game,
            objects.format,
            date_start,
            date_end,
        )
    elif objects.hub:
        data = await GetHubPairingsHistory(
            user_id,
            objects.hub,
            objects.region,
            objects.game,
            objects.format,
            date_start,
            date_end,
        )
        headers.insert(2, "Store Name")

    name = "You"
    if objects.hub:
        name = objects.hub.hub_name
    elif objects.store:
        name = objects.store.store_name


    if len(data) == 0:
        return ["No history found."]


    title = f"Personal History for {name.title()}"

    output = BuildTableOutput(title, headers, data)
    return output
