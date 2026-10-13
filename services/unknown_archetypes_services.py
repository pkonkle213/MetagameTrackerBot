from discord import Interaction, Member, Guild, User
from data.archetype_data import GetUnknownArchetypes
from services.date_functions import BuildDateRange
from checks import isMTSubmitter
from services.command_error_service import KnownError
from tuple_conversions import OutputToBuild, InteractionObjects


async def GetAllUnknown(
    objects: InteractionObjects | None,
    start_date: str,
    end_date: str,
    guild: Guild,
    user: Member,
) -> OutputToBuild:
    if not objects or not objects.store or not objects.game or not objects.format:
        raise KnownError("No Store Found")
    if not guild or isinstance(user, User):
        raise KnownError("Information was missing, cannot complete command.")
    weeks = 4 if isMTSubmitter(guild, user) else 2
    date_start, date_end = BuildDateRange(
        start_date,
        end_date,
        objects.format,
        weeks,
    )
    data = await GetUnknownArchetypes(
        objects.store.discord_id,
        objects.game.id,
        objects.format.id,
        date_start,
        date_end,
    )
    title = f"Unknown Archetypes from {date_start.strftime('%m/%d/%Y')} to {date_end.strftime('%m/%d/%Y')}"
    headers = ["Date", "Event Name", "Player Name"]
    return OutputToBuild(title, headers, data)
