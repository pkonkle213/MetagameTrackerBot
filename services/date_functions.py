from datetime import datetime, timedelta, date
from typing import Tuple
import pytz
from tuple_conversions import Format

TIMEZONE = pytz.timezone('America/New_York')


def BuildDateRange(
  start_date: str,
  end_date: str,
  format: Format | None,
  weeks: int = 8
) -> Tuple[date, date]:
  date_end = GetToday() if end_date == '' else ConvertToDate(end_date)
  date_start = GetStartDate(date_end, weeks)
  if start_date != '':
    date_start = ConvertToDate(start_date)
  elif format and format.last_ban_update and format.last_ban_update > date_start:
    date_start = format.last_ban_update
  return date_start, date_end


def DateDifference(date1, date2) -> int:
  return abs((date1 - date2).days)


def GetStartDate(end_date, weeks) -> date:
  start = end_date - timedelta(days=end_date.weekday()) - timedelta(
      weeks=weeks)
  return start


def GetWeeksAgo(date, weeks) -> date:
  return date - timedelta(weeks=weeks)


def GetDaysAgo(date, days) -> date:
  return date - timedelta(days=days)


def GetToday() -> date:
  return datetime.now(TIMEZONE).date()


def ConvertToDate(date) -> date:
  if date.count('/') == 1:
    date += '/' + str(GetToday().year)
  newDate = datetime.strptime(date, '%m/%d/%Y').date()
  return newDate
