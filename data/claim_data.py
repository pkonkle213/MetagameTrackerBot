import os
import psycopg2
from tuple_conversions import ConvertToEvent

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
      event_type,
      is_posted,
      is_complete,
      INITCAP(player_name)
    FROM
      events_view
      LEFT JOIN (
        SELECT
          event_id,
          player_name
        FROM
          full_standings
        WHERE
          UPPER(player_name) = UPPER('{player_name}')
      ) fp ON fp.event_id = id
    WHERE
      discord_id = {discord_id}
      AND game_id = {game.GameId}
      AND format_id = {format.FormatId}
      AND event_date = '{date}'
    '''
    
    cur.execute(command)
    row = cur.fetchone()
    return (ConvertToEvent(row[0:9]), row[9]) if row else (None, '')