import os
import psycopg2
from constants import Levels

def EventReportedDetails(store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.event_date,
      g.name as game_name,
      f.name as format_name,
      er.reported,
      er.total_attended,
      ROUND(reported_percent * 100, 2) as reported_percent
    FROM events_reported er
    INNER JOIN events e ON er.id = e.id
    INNER JOIN Games g ON g.id = e.game_id
    INNER JOIN formats f ON f.id = e.format_id
    WHERE er.discord_id = {store.DiscordId}
    AND e.event_date >= (CURRENT_DATE - 40)
    ORDER BY event_date desc, game_name, format_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def CheckLevel(store):
  level_definitions = []
  for level in Levels:
    level_command = f"""
    SELECT
      '{level.Number}' AS level,
      {level.NumEvents} AS num_events,
      COUNT(*) AS actual,
      {level.Percent} AS percent
    FROM
      X
    WHERE
      reported_percent >= {level.Percent}
    UNION
    """
    level_definitions.append(level_command)
  criteria = ''.join(level_definitions)[:-5]
  
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      level
    FROM
      (
        WITH
          X AS (
            SELECT
              e.event_date,
              g.name AS game_name,
              f.name AS format_name,
              er.reported,
              er.total_attended,
              ROUND(reported_percent * 100, 2) AS reported_percent
            FROM
              events_reported er
              INNER JOIN events e ON er.id = e.id
              INNER JOIN Games g ON g.id = e.game_id
              INNER JOIN formats f ON f.id = e.format_id
            WHERE
              er.discord_id = 1210746744602890310
              AND e.event_date >= (CURRENT_DATE - 40)
            ORDER BY
              event_date DESC,
              game_name,
              format_name
          )
       {criteria}
      )
    WHERE
      actual >= num_events
    ORDER BY
      level DESC
    LIMIT
      1
      '''

    cur.execute(command)
    row = cur.fetchone()
    return row[0] if row else 0