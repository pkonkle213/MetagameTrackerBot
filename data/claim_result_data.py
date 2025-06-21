import os
import psycopg2

#TODO: This needs to inject player_name as it's a string input
def AddArchetype(event_id,
                 player_name,
                 archetype_played,
                 submitter_id,
                 submitter_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO ArchetypeSubmissions
    (event_id,
    player_name,
    archetype_played,
    date_submitted,
    submitter_id,
    submitter_username,
    reported)
    VALUES
    ({event_id},
    '{player_name}',
    '{archetype_played}',
    NOW(),
    {submitter_id},
    '{submitter_name}',
    {False})
    RETURNING *
    '''
    
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

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
      (
        SELECT
          event_id,
          player_name
        FROM
          participants p
        UNION
        SELECT
          event_id,
          player1_name AS player_name
        FROM
          rounddetails rd
        UNION
        SELECT
          event_id,
          player2_name AS player_name
        FROM
          rounddetails rd
        WHERE
          player2_name != 'BYE'
      ) p
      LEFT OUTER JOIN (
        SELECT DISTINCT
          ON (event_id, player_name) event_id,
          player_name,
          archetype_played
        FROM
          ArchetypeSubmissions
        WHERE
          reported = FALSE
        ORDER BY
          event_id,
          player_name,
          id DESC
      ) X ON X.event_id = p.event_id
      AND X.player_name = p.player_name
    WHERE
      p.event_id = {event_id}    
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