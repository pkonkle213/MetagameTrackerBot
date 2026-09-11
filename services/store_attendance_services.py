from discord import Interaction
from services.date_functions import BuildDateRange
from interaction_objects import GetObjectsFromInteraction
from data.store_attendance_data import GetStoreAttendance, GetHubAttendance
from settings import DATAGUILDID
from services.command_error_service import KnownError
from tuple_conversions import OutputToBuild


def GetAttendance(
    interaction: Interaction,
    start_date: str,
    end_date: str
) -> OutputToBuild:
    objects = GetObjectsFromInteraction(interaction)
    date_start, date_end = BuildDateRange(start_date, end_date)

    headers = ["Date", "Event Name", "Players"]
    data = GetStoreAttendance(
        objects.discord_id,
        objects.category_id,
        objects.channel_id,
        date_start,
        date_end
    )
    title = f"Attendance from {date_start.strftime('%m/%d/%Y')} to {date_end.strftime('%m/%d/%Y')}"

    return OutputToBuild(title, headers, data)
