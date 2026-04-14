from tuple_conversions import League
from services.date_functions import ConvertToDate
from services.command_error_service import KnownError
from data.league_data import UpdateLeague, InsertLeague
from tuple_conversions import Store, Game, Format
from datetime import date

def ValidateLeagueInput(start_date:str,
                       end_date:str,
                       top_cut:str)->tuple[date, date,int]:
  try:
    date_start = ConvertToDate(start_date)
    date_end = ConvertToDate(end_date)
    top_cut_num = int(top_cut)
  except Exception as e:
    raise KnownError('Error creating league. Please ensure all fields are filled out with the correct formatting.')

  if date_start > date_end:
    raise KnownError('Start date must be before end date')

  return date_start, date_end, top_cut_num

def CreateLeagueInput(
  store:Store,
  game:Game,
  format:Format,
  league_name:str,
  start_date:str,
  end_date:str,
  top_cut:str,
  description:str,
  user_id:int
) -> League:
  date_start, date_end, top_cut_num = ValidateLeagueInput(start_date, end_date, top_cut)
  league = InsertLeague(league_name, description, date_start, date_end, top_cut_num, store.discord_id, game.id, format.id, user_id)
  return league

def UpdateLeagueInput(
  league:League,
  league_name:str,
  start_date:str,
  end_date:str,
  top_cut:str,
  description:str,
  user_id:int
) -> League:
  """Validates input and updates a league"""
  date_start, date_end, top_cut_num = ValidateLeagueInput(start_date, end_date, top_cut)
  league = UpdateLeague(league.id, league_name, description, date_start, date_end, top_cut_num, user_id)
  return league
  