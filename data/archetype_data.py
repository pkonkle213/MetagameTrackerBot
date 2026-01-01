from settings import DATABASE_URL
import psycopg
from psycopg.rows import class_row, namedtuple_row
from dataclasses import dataclass

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
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor(row_factory=namedtuple_row) as cur:
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
      
      cur.execute(command, criteria)  # type: ignore[arg-type]
      conn.commit()
      row = cur.fetchone()
      print(row)
      return Archetype(row[0], row[1], row[2], row[3], row[4]) if row else None

def GetUnknownArchetypes(discord_id,
                         game_id,
                         format_id,
                         start_date,
                         end_date):
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor(row_factory=namedtuple_row) as cur:
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

      cur.execute(command)  # type: ignore[arg-type]
      rows = cur.fetchall()
      
      return rows
