from settings import DATABASE_URL
import psycopg2
import psycopg2.extras
from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class Archetype:
  """Represents a submitted archetype"""
  EventId: str
  PlayerName: str
  Archetype: str
  SubmitterId: str
  SubmitterName: str

def AddArchetype(event_id,
  player_name,
  archetype_played,
  submitter_id,
  submitter_name):
  criteria = [player_name, archetype_played]
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
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
    print(row)
    return Archetype(row[0], row[1], row[2], row[3], row[4]) if row else None

def GetUnknownArchetypes(discord_id,
                         game_id,
                         format_id,
                         start_date,
                         end_date):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
    command = f'''
    SELECT
      event_date,
      player_name
    FROM
      unknown_archetypes
    WHERE
      event_date BETWEEN '{start_date}' AND '{end_date}'
      AND game_id = {game_id}
      AND format_id = {format_id}
      AND discord_id = {discord_id}
    ORDER BY
      event_date desc,
      player_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    
    return rows