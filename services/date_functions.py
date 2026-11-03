from custom_errors import KnownError
from datetime import datetime, timedelta, date
from calendar import monthrange
import pytz
from tuple_conversions import Format

TIMEZONE = pytz.timezone("America/New_York")


# TODO: Can this also return the formatting that should be used for the dates?
# If the yeras are not both equal to the current year, then we should use the full date format
# Otherwise, we can use the month/day format
def BuildDateRange(
    start_date: str,
    end_date: str,
    format: Format | None = None,
    weeks: int = 8,
    *,
    years: int | None = None,
) -> tuple[date, date]:
    date_end = GetToday() if end_date == "" else ConvertToDate(end_date)
    if years is None:
        date_start = GetStartDate(date_end, weeks)
    else:
        previous_year = date_end.year - years
        try:
            date_start = date_end.replace(year=previous_year)
        except ValueError:
            date_start = date_end.replace(
                year=previous_year,
                day=monthrange(previous_year, date_end.month)[1],
            )
    if start_date != "":
        date_start = ConvertToDate(start_date)
    elif (
        years is None
        and format
        and format.last_ban_update
        and format.last_ban_update > date_start
    ):
        date_start = format.last_ban_update
    if date_start > date_end:
        raise KnownError("The start date cannot be after the end date")
    return date_start, date_end


def DateDifference(date1: date, date2: date) -> int:
    return abs((date1 - date2).days)


def GetStartDate(end_date: date, weeks: int) -> date:
    start = end_date - timedelta(days=end_date.weekday()) - timedelta(weeks=weeks)
    return start


def GetWeeksAgo(date: date, weeks: int) -> date:
    return date - timedelta(weeks=weeks)


def GetDaysAgo(date: date, days: int) -> date:
    return date - timedelta(days=days)


def GetToday() -> date:
    return datetime.now(TIMEZONE).date()


def ConvertToDate(date: str) -> date:
    try:
        if date.count("/") == 1:
            date += "/" + str(GetToday().year)
        newDate = datetime.strptime(date, "%m/%d/%Y").date()
        return newDate
    except Exception:
        raise KnownError(
            f'Unable to convert "{date}" to a date. Please use the format MM/DD/YYYY.'
        )
