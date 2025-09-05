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
      ROUND(100 * win_percentage, 2) AS win_percentage
    FROM
      (
        SELECT
          1 AS rank,
          {"' ' AS format_name," if not format else ''}
          'OVERALL' AS archetype_played,
          sum(wins) AS wins,
          sum(losses) AS losses,
          sum(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          full_standings fp
          INNER JOIN events e ON e.id = fp.event_id
          INNER JOIN formats f ON e.format_id = f.id
          INNER JOIN player_names pn ON e.discord_id = pn.discord_id AND fp.player_name = pn.player_name
        WHERE
          pn.submitter_id = {user_id}
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
          AND e.discord_id = {discord_id}
          AND e.game_id = {game.ID}
          {f'AND e.format_id = {format.ID}' if format else ''}
        UNION
        SELECT
          2 AS rank,
          {'f.name AS format_name,' if not format else ''}
          COALESCE(archetype_played, 'UNKNOWN') AS archetype_played,
          SUM(wins) AS wins,
          SUM(losses) AS losses,
          SUM(draws) AS draws,
          1.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)) AS win_percentage
        FROM
          full_standings fp
          LEFT JOIN unique_archetypes ua ON ua.event_id = fp.event_id
          AND ua.player_name = fp.player_name
          INNER JOIN events e ON e.id = fp.event_id
          INNER JOIN formats f ON e.format_id = f.id
          INNER JOIN player_names pn ON e.discord_id = pn.discord_id AND fp.player_name = pn.player_name
        WHERE
          pn.submitter_id = {user_id}
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
          AND e.discord_id = {discord_id}
          AND e.game_id = {game.ID}
          {f'AND e.format_id = {format.ID}' if format else ''}
        GROUP BY
          {'f.name,' if not format else ''}
          archetype_played
      )
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

#TODO: I feel like there's a cleaner way to represent this and not have the same where statements repeated
#Perhaps COUNT(*) OVER (PARTITION BY e.id) AS total_events
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
                  player_name,
                  sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percentage,
                  1.0 * count(*) / (
                    SELECT
                      COUNT(*)
                    FROM
                      events
                    WHERE
                      event_date BETWEEN '{start_date}' AND '{end_date}'
                      {f'AND discord_id = {store.DiscordId}' if store.DiscordId != BOTGUILDID else ''}
                      AND game_id = {game.ID}
                      {f'AND format_id = {format.ID}' if format else ''}
                  ) AS attendance_percentage
                FROM
                  events e
                  INNER JOIN full_standings fp ON fp.event_id = e.id
                WHERE
                  event_date BETWEEN '{start_date}' AND '{end_date}'
                  {f'AND discord_id = {store.DiscordId}' if store.DiscordId != BOTGUILDID else ''}
                  AND game_id = {game.ID}
                  {f'AND format_id = {format.ID}' if format else ''}
                GROUP BY
                  player_name
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
              AND game_id = {game.ID}
              {f'AND format_id = {format.ID}' if format else ''}
            GROUP BY
              e.id
          )
      )
    ORDER BY
      player_rank
    """

    print('Leaderboard command:', command)
    cur.execute(command)
    rows = cur.fetchall()
    return rows