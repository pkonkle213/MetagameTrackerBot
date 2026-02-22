from datetime import date
from typing import Tuple
import psycopg
import psycopg2
from psycopg.rows import class_row
from settings import DATABASE_URL
from tuple_conversions import Event

def GetEvent(
  event_id: int
) -> Event:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Event)) as cur:
    command = """
    SELECT
      id,
      custom_event_id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update,
      event_type_id,
      event_name,
      reported_as
    FROM
      events_view
    WHERE
      id = %s"""
    
    criteria = [event_id]
    print('GetEvent Command:', command, criteria)
    cur.execute(command, criteria)
    row = cur.fetchone()
    if not row:
      raise Exception(f'Cannot find event. ID: {event_id}')
    print('GetEvent Row:', row)
    return row

#TODO: When I create an event, should I track when and by whom the event was created? (Answer: probably, yes)
def CreateEvent(
  event_date:date,
  discord_id:int,
  game_id:int,
  format_id:int,
  event_name:str,
  event_type_id:int,
  user_id:int
) -> int:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events
    (event_date,
    discord_id,
    game_id
    , format_id
    , last_update
    , event_name
    , event_type_id
    , created_at
    , created_by
    )
    VALUES
    ('{event_date}',
    {discord_id},
    {game_id}
    , {format_id}
    , 0
    , '{event_name}'
    , {event_type_id}
    , CURRENT_TIMESTAMP AT TIME ZONE 'America/New_York'
    , {user_id}
    )
    RETURNING id
    '''

    cur.execute(command)
    conn.commit()
    event_id = cur.fetchone()
    print('Event ID received:', event_id)
    if not event_id:
      raise Exception('Unable to create event')
    return event_id[0]

def GetEventMeta(event_id) -> list[Tuple[str,int,int,int]]:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      INITCAP(COALESCE(archetype_played, 'UNKNOWN')) AS archetype_played,
      wins,
      losses,
      draws
    FROM
      full_standings fp
      LEFT JOIN unique_archetypes ua ON ua.event_id = fp.event_id
      AND UPPER(ua.player_name) = UPPER(fp.player_name)
    WHERE
      fp.event_id = {event_id}
    ORDER BY
      wins DESC,
      draws DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def DeleteStandingsFromEvent(event_id):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM standings
    WHERE event_id = {event_id}
    '''

    cur.execute(command)
    conn.commit()
    return True
  