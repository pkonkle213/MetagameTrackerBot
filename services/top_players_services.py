from discord import Interaction
from services.date_functions import BuildDateRange
from data.player_data import GetTopPlayerData
from services.command_error_service import KnownError
from tuple_conversions import OutputToBuild, InteractionObjects


async def GetTopPlayers(
    objects: InteractionObjects | None, start_date: str, end_date: str
) -> OutputToBuild:
    if not objects or not objects.store or not objects.game:
        raise KnownError("Unable to find store or game")

    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

    data = await GetTopPlayerData(
        objects.store, objects.game, objects.format, date_start, date_end
    )
    title = f"Top Players from {date_start.strftime('%B %d')} to {date_end.strftime('%B %d')}"
    headers = ["Rank", "Name", "Points", "Win %"]
    return OutputToBuild(title, headers, data)
