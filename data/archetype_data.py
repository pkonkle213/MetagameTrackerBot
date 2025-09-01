import os
import psycopg2

from tuple_conversions import ConvertToArchetype

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
    RETURNING event_id,
    player_name,
    archetype_played,
    submitter_id,
    submitter_username
    '''
    
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return ConvertToArchetype(row) if row else None

def GetUnknownArchetypes(discord_id, game_id, format_id, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      event_date,
      player_name
    FROM unknownarchetypes
    WHERE
      event_date BETWEEN '{start_date}' AND '{end_date}'
      AND game_id = {game_id}
      AND format_id = {format_id}
      AND discord_id = {discord_id}
    ORDER BY event_date desc, player_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows