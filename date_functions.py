from datetime import datetime, timedelta
import pytz

def FormatDate(date):
  return date.strftime('%B %d')

def GetCurrentQuarter():
  now = datetime.now(pytz.timezone('America/New_York'))
  return (now.year, (now.month + 2) // 3)

def GetQuarterRange(year, quarter):
  if year != 0 and quarter == 0:
    year = datetime.now(pytz.timezone('America/New_York')).year
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
  else:
    if year == 0 and quarter != 0:
      year = datetime.now(pytz.timezone('America/New_York')).year
    
    if year == 0 and quarter == 0:
      year, quarter = GetCurrentQuarter()
    
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

def GetWeeksAgo(date, weeks):
  return date - timedelta(weeks=weeks)

def GetDaysAgo(date, days):
  return date - timedelta(days=days)

def GetToday():
  return datetime.now(pytz.timezone('US/Eastern')).date()

def convert_to_date(date):
  if date.count('/') == 1:
    date += '/' + str(GetToday().year)
  try:
    newDate = datetime.strptime(date, '%m/%d/%Y').date()
    return newDate
  except ValueError:
    return None

def FindMonday():
  def to_last_monday(date):
    day_of_week = date.weekday()
    days_to_subtract = day_of_week if day_of_week != 0 else 7
    return date - datetime.timedelta(days=days_to_subtract)
  
  today = datetime.date.today()
  last_monday = to_last_monday(today)
  print(last_monday)