import psycopg2
from typing import Any
from datetime import date
from custom_errors import KnownError
from models.event import Event
from models.format import Format
from models.game import Game
from settings import DATABASE_URL

def EventIsPosted(event_id:int) -> bool:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET is_posted = TRUE
    WHERE id = {event_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return True if row else False
    
def GetEvent(discord_id:int,
             date:date,
             game:Game,
             format:Format) -> Event | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update,
      event_type
    FROM
      events_view
    WHERE
      discord_id = {discord_id}
      AND game_id = {game.GameId}
      AND format_id = {format.FormatId}
      AND event_date = '{date}'
    ORDER BY
      event_date DESC
    LIMIT
      1
    '''
    
    cur.execute(command)
    row = cur.fetchone()
  
    return Event(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) if row else None

def CreateEvent(event_date:date,
                discord_id:int,
                game:Game,
                format:Format) -> Event:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events
    (event_date,
    discord_id,
    game_id
    , format_id
    , last_update
    )
    VALUES
    ('{event_date}',
    {discord_id},
    {game.GameId}
    , {format.FormatId}
    , 0
    )
    RETURNING event_id
    '''
    
    cur.execute(command)
    conn.commit()
    event = cur.fetchone()
    if event is None:
      raise KnownError('There was an error creating the event')
    return GetEventById(event[0])

def GetEventById(event_id:int) -> Event:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update,
      event_type
    FROM
      events_view
    WHERE
      id = {event_id}
    '''
    
    cur.execute(command)
    row = cur.fetchone()
    if row is None:
      raise KnownError('Unable to find event')
    return Event(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

def GetEventMeta(event_id:int) -> list[tuple[Any, ...]]:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      COALESCE(archetype_played, 'UNKNOWN') AS archetype_played,
      wins,
      losses,
      draws
    FROM
      full_standings fp
      LEFT JOIN unique_archetypes ua ON ua.event_id = fp.event_id
      AND ua.player_name = fp.player_name
    WHERE
      fp.event_id = {event_id}
    ORDER BY
      wins DESC,
      draws DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def DeleteStandingsFromEvent(event_id:int):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM standings
    WHERE event_id = {event_id}
    RETURNING TRUE
    '''

    cur.execute(command)
    conn.commit()
    return True
  