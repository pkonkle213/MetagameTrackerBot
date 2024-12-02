from datetime import datetime, timedelta
import pytz

def GetQuarterRange(year, quarter):
  start_month = 1 + 3 * (quarter - 1)
  start_date = datetime(year, start_month, 1).date()
  next_start_month = start_month + 3
  if next_start_month > 12:
    year += 1
    next_start_month = 1
  next_month = datetime(year, next_start_month, 1).date()
  end_date = next_month - timedelta(days=1)
  return (start_date, end_date)
  
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