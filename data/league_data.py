from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from tuple_conversions import League
from datetime import date
from psycopg.rows import class_row

def GetLeagues(discord_id:int, game_id:int, format_id:int) -> list[League]:
  conn =  psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(League)) as cur:
    command = f'''
    SELECT *
    FROM leagues
    WHERE discord_id = %s
    AND game_id = %s
    AND format_id = %s
    ORDER BY end_date DESC, start_date DESC
    '''
    cur.execute(command, [discord_id, game_id, format_id])
    rows = cur.fetchall()
    return rows

def UpdateLeague(
  league_id:int,
  league_name:str,
  description:str,
  start_date:date,
  end_date:date,
  top_cut:int,
  user_id:int
) -> League:
  conn =  psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(League)) as cur:
    command = f'''
    UPDATE leagues
    SET
      name = %s,
      description = %s,
      start_date = %s,
      end_date = %s,
      top_cut = %s,
      last_update = NOW(),
      updated_by = %s
    WHERE id = %s
    RETURNING *
    '''
    criteria = [league_name, description, start_date, end_date, top_cut, user_id, league_id]
    cur.execute(command, criteria)
    row = cur.fetchone()
    if not row:
      raise KnownError('Unable to update league')
    return row

def InsertLeague(
  league_name:str,
  description:str,
  start_date:date,
  end_date:date,
  top_cut:int,
  store_id:int,
  game_id:int,
  format_id:int,
  user_id:int
) -> League:
  conn =  psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(League)) as cur:
    command = f'''
    INSERT INTO leagues (
      name,
      description,
      start_date,
      end_date,
      top_cut,
      discord_id,
      game_id,
      format_id,
      created_by,
      date_created
    )
    VALUES (
      %s,
      %s,
      %s,
      %s,
      %s,
      %s,
      %s,
      %s,
      %s,
      NOW()
    )
    RETURNING *
    '''

    criteria = [league_name, description, start_date, end_date, top_cut, store_id, game_id, format_id, user_id]
    cur.execute(command, criteria)
    row = cur.fetchone()
    if not row:
      raise KnownError('Unable to create league')
    return row