from datetime import date, datetime, timedelta
import pytz
from models.format import Format

def BuildDateRange(start_date:str, end_date:str, format:Format | None, weeks:int = 8) -> tuple[date,date]:
  date_end = GetToday() if end_date == '' else ConvertToDate(end_date)
  date_start = GetStartDate(date_end, weeks)
  if start_date != '':
    date_start = ConvertToDate(start_date)
  elif format and format.LastBanUpdate  and format.LastBanUpdate > date_start:
    date_start = format.LastBanUpdate
  return date_start, date_end

def DateDifference(date1:date, date2:date) -> int:
  return abs((date1 - date2).days)
  
def GetStartDate(end_date:date, weeks:int) -> date:
  start = end_date - timedelta(days=end_date.weekday()) - timedelta(weeks=weeks)
  return start

def GetWeeksAgo(date:date, weeks:int) -> date:
  return date - timedelta(weeks=weeks)

def GetDaysAgo(date:date, days:int) -> date:
  return date - timedelta(days=days)

def GetToday() -> date:
  return datetime.now(pytz.timezone('US/Eastern')).date()

def ConvertToDate(date:str) -> date:
  if date.count('/') == 1:
    date += '/' + str(GetToday().year)
  newDate = datetime.strptime(date, '%m/%d/%Y').date()
  return newDate
  