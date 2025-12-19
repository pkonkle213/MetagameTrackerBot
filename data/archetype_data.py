from datetime import date
from settings import DATABASE_URL
import psycopg2
from models.archetype import Archetype
from models.unknownArchetype import Unknown
from data.sql.readSQL import read_sql_file

NewArchetype = "NewArchetype.sql"

def AddArchetype(event_id:int,
  player_name:str,
  archetype_played:str,
  submitter_id:int,
  submitter_name:str) -> Archetype | None:
  """Adds the archetype to the database"""
  criteria = [event_id, player_name, archetype_played, submitter_id, submitter_name]
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = read_sql_file(NewArchetype)
    
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return Archetype(row[0], row[1], row[2], row[3], row[4]) if row else None

def GetUnknownArchetypes(discord_id:int,
                         game_id:int,
                         format_id:int,
                         start_date:date,
                         end_date:date) -> list[Unknown]:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      event_date,
      player_name
    FROM unknown_archetypes
    WHERE
      event_date BETWEEN '{start_date}' AND '{end_date}'
      AND game_id = {game_id}
      AND format_id = {format_id}
      AND discord_id = {discord_id}
    ORDER BY event_date desc, player_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return [Unknown(row[0], row[1]) for row in rows]