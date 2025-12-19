import os
import psycopg2

def GetStoreReportedPercentage(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      e.event_date,
      s.store_name,
      g.name as game_name,
      f.name as format_name,
      er.reported,
      er.total_attended,
      ROUND(100.0 * reported_percent, 2) AS reported_percent
    FROM
      events_reported er
      INNER JOIN events e ON er.id = e.id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
    {f'WHERE e.discord_id = {discord_id}' if discord_id != 0 else f'WHERE s.used_for_data = {True}'}
    ORDER BY
      e.event_date DESC,
      s.store_name,
      f.name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows
