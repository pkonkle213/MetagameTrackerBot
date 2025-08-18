import os
import psycopg2

def GetEventReportedPercentage(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      COUNT(
        CASE
          WHEN archetype_played IS NOT NULL THEN 1
        END
      ) / SUM(count(*)) OVER () AS percentage
    FROM
      fullparticipants fp
      LEFT OUTER JOIN uniquearchetypes ua ON ua.event_id = fp.event_id
      AND ua.player_name = fp.player_name
    WHERE
      fp.event_id = {event_id}
    """
    
    cur.execute(command)
    row = cur.fetchone()
    return row[0] if row else None

def UpdateEvent(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET last_update = last_update + 1
    WHERE id = {event_id}
    RETURNING *
    '''
    
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row