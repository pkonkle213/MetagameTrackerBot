from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from tuple_conversions import League
from datetime import date
from psycopg.rows import class_row
from tuple_conversions import TopPlayers

def GetLeagueLeaderboard(league:League) -> list[TopPlayers]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(TopPlayers)) as cur:
    command = f'''
    WITH
      X AS (
        SELECT
          INITCAP(player_name) AS player_name,
          wins,
          losses,
          draws
        FROM
          full_standings fs
          INNER JOIN events e ON fs.event_id = e.id
          INNER JOIN stores_view s ON e.discord_id = s.discord_id
        WHERE
          e.league_id = {league.id}
      )
    SELECT
      player_name,
      (3 * SUM(wins) + SUM(draws)) AS points,
      ROUND(
        100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)),
        2
      ) AS win_percent
    FROM
      X
    GROUP BY
      player_name
    ORDER BY
      2 DESC,
      3 DESC,
      1
    LIMIT
      {league.top_cut}
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

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