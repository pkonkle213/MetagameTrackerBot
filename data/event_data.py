import os
import psycopg2

from tuple_conversions import ConvertToEvent

def EventIsComplete(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET is_complete = TRUE
    WHERE id = {event_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

def EventIsPosted(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
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
    return row
    
def GetEvent(discord_id,
                date,
                game,
                format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update,
      event_type,
      COALESCE(is_posted, {False}) as is_posted,
      COALESCE(is_complete, {False}) as is_complete
    FROM
      events_view
    WHERE
      discord_id = {discord_id}
      AND game_id = {game.ID}
      AND format_id = {format.ID}
      AND event_date = '{date}'
    ORDER BY
      event_date DESC
    LIMIT
      1
    '''
    
    cur.execute(command)
    row = cur.fetchone()
    return ConvertToEvent(row) if row else None

def CreateEvent(event_date,
  discord_id,
  game,
  format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events
    (event_date,
    discord_id,
    game_id
    {', format_id' if game.HasFormats else ''}
    , last_update
    , is_posted
    , is_complete
    )
    VALUES
    ('{event_date}',
    {discord_id},
    {game.ID}
    {f' , {format.ID}' if game.HasFormats else ''}
    , 0
    , {False}
    , {False}
    )
    RETURNING
    id, discord_id, event_date, game_id, format_id, 0, '{None}', {False}, {False}
    '''
    
    cur.execute(command)
    conn.commit()
    event = cur.fetchone()
    return ConvertToEvent(event) if event else None

def GetEventMeta(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
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

def DeleteStandingsFromEvent(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM standings
    WHERE event_id = {event_id}
    '''

    cur.execute(command)
    conn.commit()
    return True
  