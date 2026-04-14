from datetime import date
from typing import Tuple
import psycopg
from psycopg.rows import class_row, scalar_row
from settings import DATABASE_URL
from tuple_conversions import Event, EventInput

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
      reported_as,
      league_id,
      created_by,
      created_at
    FROM
      events_view
    WHERE
      id = %s
    """
    
    criteria = [event_id]
    cur.execute(command, criteria)
    row = cur.fetchone()
    if not row:
      raise Exception(f'Cannot find event. ID: {event_id}')
    return row

def CreateEvent(
  event:EventInput,
  user_id:int
) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
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
    , league_id
    )
    VALUES
    ('{event.event_date}',
    {event.StoreID},
    {event.GameID}
    , {event.FormatID}
    , 0
    , '{event.event_name}'
    , {event.event_type_id if event.event_type_id > 0 else 3}
    , CURRENT_TIMESTAMP AT TIME ZONE 'America/New_York'
    , {user_id}
    {f', {-event.event_type_id}' if event.event_type_id < 0 else ', NULL'}
    )
    RETURNING id
    '''

    cur.execute(command)
    conn.commit()
    event_id = cur.fetchone()
    
    if not event_id:
      raise Exception('Unable to create event')
    return event_id

def GetEventDetails(event_id:int) -> list[Tuple[str,int,int,int]]:
  conn = psycopg.connect(DATABASE_URL)
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
      2 DESC,
      4 DESC,
      1 DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def DeleteStandingsFromEvent(event_id):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM standings
    WHERE event_id = {event_id}
    '''

    cur.execute(command)
    conn.commit()
    return True
  