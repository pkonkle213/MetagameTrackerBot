import os
import psycopg2

def GetStoreReportedPercentage(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      e.event_date,
      s.store_name,
      f.name,
      er.reported,
      er.total_attended,
      ROUND(100.0 * reported_percent, 2) AS reported_percent
    FROM
      events_reported er
      INNER JOIN events e ON er.id = e.id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
    {f'WHERE e.discord_id = {discord_id}' if discord_id != 0 else f'WHERE s.used_for_data = {True}'}
    GROUP BY
      e.event_date,
      s.store_name,
      f.name
    ORDER BY
      e.event_date DESC,
      s.store_name,
      f.name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def EventsAboveThreshold(percent, num_expected, date=None):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      er.discord_id
    FROM
      events_reported er
      INNER JOIN events e ON e.id = er.id
      INNER JOIN stores s ON er.discord_id = s.discord_id
    WHERE
      e.event_date BETWEEN {'CURRENT_DATE' if date is None else f"DATE('{date}')"} - 40 AND {'CURRENT_DATE' if date is None else f"DATE('{date}')"}
      AND s.last_payment > CURRENT_DATE - INTERVAL '1 month'
    GROUP BY
      er.discord_id
    HAVING
      COUNT(
        CASE
          WHEN reported_percent >= {percent} THEN 1
        END
      ) >= {num_expected}
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows