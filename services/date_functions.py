from datetime import datetime, timedelta
import pytz

from tuple_conversions import Format

TIMEZONE = pytz.timezone('America/New_York')


def BuildDateRange(start_date: str,
                   end_date: str,
                   format: Format,
                   weeks: int = 8):
  date_end = GetToday() if end_date == '' else ConvertToDate(end_date)
  date_start = GetStartDate(date_end, weeks)
  if start_date != '':
    date_start = ConvertToDate(start_date)
  elif format.LastBanUpdate is not None and format.LastBanUpdate > date_start:
    date_start = format.LastBanUpdate
  return date_start, date_end


def DateDifference(date1, date2):
  return abs((date1 - date2).days)


def GetStartDate(end_date, weeks):
  start = end_date - timedelta(days=end_date.weekday()) - timedelta(
      weeks=weeks)
  return start


def GetWeeksAgo(date, weeks):
  return date - timedelta(weeks=weeks)


def GetDaysAgo(date, days):
  return date - timedelta(days=days)


def GetToday():
  return datetime.now(TIMEZONE).date()


def ConvertToDate(date):
  if date.count('/') == 1:
    date += '/' + str(GetToday().year)
  newDate = datetime.strptime(date, '%m/%d/%Y').date()
  return newDate
