import os
import psycopg2
from settings import DATABASE_URL
from tuple_conversions import ConvertToEvent, Event

def GetEvent(
  discord_id,
  date,
  game,
  format
) -> Event | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      {'format_id,' if format else ''}
      last_update,
      event_type,
    FROM
      events_view
    WHERE
      discord_id = {discord_id}
      AND game_id = {game.GameId}
      {f'AND format_id = {format.FormatId}' if format else ''}
      AND event_date = '{date}'
    ORDER BY
      event_date DESC
    LIMIT
      1
    '''
    
    cur.execute(command)
    row = cur.fetchone()
    return ConvertToEvent(row) if row else None

#TODO: Save point - Need to add event_type and just return the ID for the event to know it was created
def CreateEvent(event_date,
  discord_id,
  game,
  format):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events
    (event_date,
    discord_id,
    game_id
    {', format_id' if format else ''}
    , last_update
    , is_posted
    , is_complete
    )
    VALUES
    ('{event_date}',
    {discord_id},
    {game.GameId}
    {f' , {format.FormatId}' if format else ''}
    , 0
    , {False}
    , {False}
    )
    RETURNING
    id
    '''
    
    cur.execute(command)
    conn.commit()
    event_id = cur.fetchone()
    return event_id

def GetEventMeta(event_id):
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
  