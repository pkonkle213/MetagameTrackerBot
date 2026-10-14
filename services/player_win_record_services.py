from tuple_conversions import InteractionObjects
from discord import Interaction
from data.player_data import GetStats
from services.date_functions import BuildDateRange


async def PlayRecord(
    start_date: str, end_date: str, objects: InteractionObjects | None, user_id: int
):
    if not objects or not objects.store or not objects.game:
        raise Exception("No store or game found")
    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
    data = await GetStats(
        objects.store.discord_id,
        objects.game,
        objects.format,
        user_id,
        date_start,
        date_end,
    )
    title = f"Your Results From {date_start.strftime('%m/%d/%Y')} To {date_end.strftime('%m/%d/%Y')}"
    header = ["Archetype Name", "Wins", "Losses", "Draws", "Win %"]
    if not format:
        header.insert(0, "Format")
    return (data, title, header)
