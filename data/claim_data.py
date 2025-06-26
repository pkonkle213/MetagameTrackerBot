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
      player_name
    FROM
      (
        SELECT
          e.id,
         e.discord_id,
         e.event_date,
     e.game_id,
     e.format_id,
     e.last_update
        FROM
          events e
        WHERE
          e.discord_id = {discord_id}
          AND e.game_id = {game.ID}
          AND e.format_id = {format.ID}
          AND e.event_date = '{date}'
      ) e
      LEFT JOIN (
        SELECT
          event_id,
          player_name
        FROM
          fullparticipants
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
                            '')