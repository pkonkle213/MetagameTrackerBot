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
      COUNT(*) FILTER (
        WHERE
          archetype_played IS NOT NULL
      ) AS reported,
      COUNT(*) AS total_attended,
      ROUND(
        100.0 * COUNT(*) FILTER (
          WHERE
            archetype_played IS NOT NULL
        ) / COUNT(*),
        2
      ) AS reported_percent
    FROM
      (
        SELECT
          e.id,
          asu.archetype_played
        FROM
          Events e
          INNER JOIN fullparticipants fp ON fp.event_id = e.id
          LEFT JOIN uniquearchetypes asu ON asu.event_id = e.id
          AND asu.player_name = fp.player_name
        ORDER BY
          e.id DESC
      ) x
      INNER JOIN events e ON x.id = e.id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
    {f'WHERE e.discord_id = {discord_id}' if discord_id != 0 else ''}
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