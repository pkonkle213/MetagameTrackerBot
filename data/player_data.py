from psycopg.rows import class_row
from typing import NamedTuple
from datetime import date
from settings import DATABASE_URL, DATAGUILDID
import psycopg
from settings import BOTGUILDID
from tuple_conversions import Format, Game, Store, League, TopPlayers

#TODO: Implement this for cleaner code
class PersonalStats(NamedTuple):
  format_name: str
  archetype_played: str
  wins: int
  losses: int
  draws: int
  win_percentage: float
  
def GetStats(
  discord_id:int,
  game:Game,
  format:Format | None,
  user_id:int,
  start_date:date,
  end_date:date):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      {'format_name,' if not format else ''}
      archetype_played,
      wins,
      losses,
      draws,
      ROUND(win_percentage * 100, 2) AS win_percentage
    FROM
      (
        WITH
          X AS (
            SELECT
              fs.event_id,
              f.format_name AS format_name,
              UPPER(fs.player_name) AS player_name,
              archetype_played,
              wins,
              losses,
              draws
            FROM
              full_standings fs
              LEFT JOIN unique_archetypes ua ON UPPER(ua.player_name) = UPPER(fs.player_name)
              AND ua.event_id = fs.event_id
              LEFT JOIN events e ON e.id = fs.event_id
              LEFT JOIN formats f ON e.format_id = f.id
            WHERE
              UPPER(fs.player_name) IN (
                SELECT
                  UPPER(player_name) as player_name
                FROM
                  player_names
                WHERE
                  discord_id = {discord_id}
                  AND submitter_id = {user_id}
              )
              {f'AND e.format_id = {format.id}' if format else ''}
              AND e.game_id = {game.id}
              AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
              AND e.discord_id = {discord_id}
          )
        SELECT
          '1' AS rank,
          ' ' AS format_name,
          'Overall' AS archetype_played,
          SUM(wins) AS wins,
          SUM(losses) AS losses,
          SUM(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          X
        UNION
        SELECT
          '2' AS rank,
          format_name,
          COALESCE(INITCAP(archetype_played), 'UNKNOWN') AS archetype_played,
          SUM(wins) AS wins,
          SUM(losses) AS losses,
          SUM(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          X
        GROUP BY
          INITCAP(archetype_played),
          X.format_name
      )
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetTopPlayerData(
  store:Store,
  game:Game | None,
  format:Format | None,
  start_date:date,
  end_date:date
):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(TopPlayers)) as cur:
    command = f"""
    WITH
      X AS (
        SELECT
          fs.event_id,
          INITCAP(player_name) AS player_name,
          wins,
          losses,
          draws
        FROM
          full_standings fs
          INNER JOIN events e ON fs.event_id = e.id
          INNER JOIN stores_view s ON e.discord_id = s.discord_id
        WHERE
          e.event_date BETWEEN '{start_date}' AND '{end_date}'
          {f'AND e.format_id = {format.id}' if format else ''}
          {f'AND e.game_id = {game.id}' if game else ''}
          AND s.discord_id = {store.discord_id}
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
      CEIL(
        .5 * (
          SELECT
            AVG(participants) AS average_participants
          FROM
            (
              SELECT
                count(*) AS participants
              FROM
                X
              GROUP BY
                event_id
            )
        )
      )
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows