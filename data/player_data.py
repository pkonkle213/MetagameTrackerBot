from datetime import date
from settings import DATABASE_URL
import psycopg
from settings import BOTGUILDID
from tuple_conversions import Format, Game, Store

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
              {f'AND e.format_id = {format.format_id}' if format else ''}
              AND e.game_id = {game.game_id}
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

#TODO: Can this be simpler?
def GetTopPlayerData(
  store:Store,
  game:Game,
  format:Format | None,
  start_date:date,
  end_date:date
):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      player_name,
      round(attendance_percentage * 100, 2) AS attendance_percentage,
      round(win_percentage * 100, 2) AS win_percentage
    FROM
      (
        SELECT
          INITCAP(player_name) AS player_name,
          sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percentage,
          1.0 * COUNT(*) / (
            SELECT
              COUNT(*)
            FROM
              events
            WHERE
              event_date BETWEEN '2026-01-01' AND '2026-04-01'
              AND discord_id = 1210746744602890310
              AND game_id = 1
              AND format_id = 1
          ) AS attendance_percentage
        FROM
          events e
          INNER JOIN full_standings fp ON fp.event_id = e.id
        WHERE
          event_date BETWEEN '{start_date}' AND '{end_date}'
          {f'AND discord_id = {store.discord_id}' if store.discord_id != BOTGUILDID else ''}
          AND game_id = {game.game_id}
          {f'AND format_id = {format.format_id}' if format else ''}
        GROUP BY
          INITCAP(player_name)
      )
    ORDER BY
      attendance_percentage * win_percentage DESC
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
                events e
                LEFT JOIN full_standings fp ON fp.event_id = e.id
              WHERE
                event_date BETWEEN '{start_date}' AND '{end_date}'
                {f'AND discord_id = {store.discord_id}' if store.discord_id != BOTGUILDID else ''}
                AND game_id = {game.game_id}
                {f'AND format_id = {format.format_id}' if format else ''}
              GROUP BY
                e.id
            )
        )
      )
    """
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows