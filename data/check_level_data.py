import os
import psycopg2

def CheckLevel(store):
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
    INNER JOIN cardgames g ON g.id = e.game_id
    INNER JOIN formats f ON f.id = e.format_id
    WHERE er.discord_id = {store.DiscordId}
    AND e.event_date >= (CURRENT_DATE - 40)
    ORDER BY event_date desc, game_name, format_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows