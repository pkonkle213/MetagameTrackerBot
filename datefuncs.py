from datetime import datetime, timedelta
import pytz

def GetQuarterDate():
  today = datetime.now(pytz.timezone('US/Eastern')).date()
  start = (today.month - 1) // 3 * 3 + 1
  start_date = datetime(today.year, start, 1).date()
  return start_date

def GetStartDate(end_date):
  start = end_date - timedelta(days=end_date.weekday()) - timedelta(weeks=8)
  return start

def GetEndDate():
  today = datetime.now(pytz.timezone('US/Eastern')).date()
  return today

def convert_to_date(date):
  if date.count('/') == 1:
    date += '/2024'

  try:
    newDate = datetime.strptime(date, '%m/%d/%Y').date()
    return newDate
  except ValueError:
    return None