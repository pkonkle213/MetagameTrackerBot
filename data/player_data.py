import os
import psycopg2
from settings import BOTGUILDID

def GetStats(discord_id,
             game,
             format,
             user_id,
             start_date,
             end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
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
              f.name AS format_name,
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
                  player_name
                FROM
                  player_names
                WHERE
                  discord_id = {discord_id}
                  AND submitter_id = {user_id}
              )
              {f'AND e.format_id = {format.FormatId}' if format else ''}
              AND e.game_id = {game.GameId}
              AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
              AND e.discord_id = {discord_id}
          )
        SELECT
          '1' AS rank,
          ' ' AS format_name,
          'OVERALL' AS archetype_played,
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
          COALESCE(UPPER(archetype_played), 'UNKNOWN') AS archetype_played,
          SUM(wins) AS wins,
          SUM(losses) AS losses,
          SUM(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          X
        GROUP BY
          UPPER(archetype_played),
          X.format_name
      )
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetTopPlayerData(store,
                     game,
                     format,
                     start_date,
                     end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      player_name,
      attendance_percentage,
      win_percentage
    FROM
      (
        SELECT
          ROW_NUMBER() OVER (
            ORDER BY
              Combined DESC
          ) AS player_rank,
          player_name,
          round(attendance_percentage * 100, 2) AS attendance_percentage,
          round(win_percentage * 100, 2) AS win_percentage,
          round(attendance_percentage * win_percentage * 100, 2) AS Combined
        FROM
          (
            SELECT
              player_name,
              attendance_percentage,
              win_percentage,
              attendance_percentage * win_percentage AS Combined
            FROM
              (
                SELECT
                  UPPER(player_name) as player_name,
                  sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percentage,
                  1.0 * count(*) / (
                    SELECT
                      COUNT(*)
                    FROM
                      events
                    WHERE
                      event_date BETWEEN '{start_date}' AND '{end_date}'
                      {f'AND discord_id = {store.DiscordId}' if store.DiscordId != BOTGUILDID else ''}
                      AND game_id = {game.GameId}
                      {f'AND format_id = {format.FormatId}' if format else ''}
                  ) AS attendance_percentage
                FROM
                  events e
                  INNER JOIN full_standings fp ON fp.event_id = e.id
                WHERE
                  event_date BETWEEN '{start_date}' AND '{end_date}'
                  {f'AND discord_id = {store.DiscordId}' if store.DiscordId != BOTGUILDID else ''}
                  AND game_id = {game.GameId}
                  {f'AND format_id = {format.FormatId}' if format else ''}
                GROUP BY
                  UPPER(player_name)
              )
          )
      )
    WHERE
      player_rank < .5 * (
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
              {f'AND discord_id = {store.DiscordId}' if store.DiscordId != BOTGUILDID else ''}
              AND game_id = {game.GameId}
              {f'AND format_id = {format.FormatId}' if format else ''}
            GROUP BY
              e.id
          )
      )
    ORDER BY
      player_rank
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows