import os
import psycopg2

def GetEventAndPlayerName(discord_id, date, game, format, player_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update,
      player_name,
      event_type
    FROM
      (
       SELECT
          e.id,
          e.discord_id,
          e.event_date,
          e.game_id,
          e.format_id,
          e.last_update,
          CASE
            WHEN COUNT(round_number) > 0 THEN 'PAIRINGS'
            WHEN COUNT(player_name) > 0 THEN 'STANDINGS'
          END AS event_type
        FROM
          events e
          LEFT JOIN pairings p ON p.event_id = e.id
          LEFT JOIN standings s ON s.event_id = e.id
        WHERE
          e.discord_id = {discord_id}
          AND e.game_id = {game.ID}
          AND e.format_id = {format.ID}
          AND e.event_date = '{date}'
        GROUP BY
          e.id
      ) e
      LEFT JOIN (
        SELECT
          event_id,
          player_name
        FROM
          full_standings
        WHERE
          player_name = '{player_name}'
      ) fp ON fp.event_id = e.id
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row if row else (None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            '')