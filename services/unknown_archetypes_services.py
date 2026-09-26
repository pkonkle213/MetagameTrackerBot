from discord import Interaction, User
from data.archetype_data import GetUnknownArchetypes
from data.interaction_data import GetObjectsFromInteraction
from services.date_functions import BuildDateRange
from checks import isSubmitter
from services.command_error_service import KnownError
from tuple_conversions import OutputToBuild


async def GetAllUnknown(
    interaction: Interaction, start_date: str, end_date: str
) -> OutputToBuild:
    objects = await GetObjectsFromInteraction(interaction)
    if not objects.store or not objects.game or not objects.format:
        raise KnownError("No Store Found")
    if not interaction.guild or isinstance(interaction.user, User):
        raise KnownError("Information was missing, cannot complete command.")
    weeks = 4 if isSubmitter(interaction.guild, interaction.user, "MTSubmitter") else 2
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
