import os
import psycopg2

def AddArchetype(event_id,
  player_name,
  archetype_played,
  submitter_id,
  submitter_name):
  criteria = [player_name, archetype_played]
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
    %s,
    %s,
    NOW(),
    {submitter_id},
    '{submitter_name}',
    {False})
    RETURNING *
    '''
    
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return row

def GetUnknownArchetypes(discord_id, game_id, format_id, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      e.event_date,
      p.player_name
    FROM
      (
        SELECT
          event_id,
          p.player_name
        FROM
          participants p
        UNION
        SELECT
          event_id,
          player1_name AS player_name
        FROM
          rounddetails
        UNION
        SELECT
          event_id,
          player2_name AS player_name
        FROM
          rounddetails
        WHERE player2_name != 'BYE'
      ) p
      INNER JOIN events e ON p.event_id = e.id
      LEFT JOIN (
        SELECT DISTINCT ON (event_id, player_name)
          event_id,
          player_name,
          archetype_played,
          submitter_id
        FROM
          ArchetypeSubmissions
        WHERE
          reported = FALSE
        ORDER BY
          event_id,
          player_name,
          id DESC
      ) ap ON p.event_id = ap.event_id
      AND p.player_name = ap.player_name
    WHERE
      archetype_played IS NULL
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game_id}
      AND e.format_id = {format_id}
      AND e.discord_id = {discord_id}
    ORDER BY e.event_date desc, player_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows