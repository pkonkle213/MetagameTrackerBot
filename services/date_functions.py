from datetime import datetime, timedelta
import pytz

def BuildDateRange(start_date, end_date, format, weeks=8):
  date_end = GetToday() if end_date == '' else ConvertToDate(end_date)
  date_start = GetStartDate(date_end, weeks)
  if start_date != '':
    date_start = ConvertToDate(start_date)
  elif format is not None and format.LastBanUpdate is not None and format.LastBanUpdate > date_start:
    date_start = format.LastBanUpdate
  return date_start, date_end

def DateDifference(date1, date2):
  return abs((date1 - date2).days)

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
  
def GetStartDate(end_date, weeks):
  start = end_date - timedelta(days=end_date.weekday()) - timedelta(weeks=weeks)
  return start

def GetWeeksAgo(date, weeks):
  return date - timedelta(weeks=weeks)

def GetDaysAgo(date, days):
  return date - timedelta(days=days)

def GetToday():
  return datetime.now(pytz.timezone('US/Eastern')).date()

def ConvertToDate(date):
  if date.count('/') == 1:
    date += '/' + str(GetToday().year)
  newDate = datetime.strptime(date, '%m/%d/%Y').date()
  return newDate
  