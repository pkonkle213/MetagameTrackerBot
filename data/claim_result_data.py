from settings import DATABASE_URL
import psycopg

def GetEventReportedPercentage(event_id:int) -> float:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      COUNT(
        CASE
          WHEN archetype_played IS NOT NULL THEN 1
        END
      ) / SUM(count(*)) OVER () AS percentage
    FROM
      full_standings fp
      LEFT OUTER JOIN unique_archetypes ua ON ua.event_id = fp.event_id
      AND UPPER(ua.player_name) = UPPER(fp.player_name)
    WHERE
      fp.event_id = {event_id}
    """
    
    cur.execute(command)
    row = cur.fetchone()
    if not row:
      raise Exception('Unable to get event reported percentage')
    return row[0]

def UpdateEvent(event_id:int) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET last_update = last_update + 1
    WHERE id = {event_id}
    RETURNING id
    '''
    
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    if not row:
      raise Exception('Unable to update event')
    return row[0]