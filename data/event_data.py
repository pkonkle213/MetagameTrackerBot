import os
import psycopg2

from tuple_conversions import ConvertToEvent

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
      last_update
    FROM events e
    WHERE e.discord_id = {discord_id}
      AND e.game_id = {game.ID}
      AND e.format_id = {format.ID}
      AND e.event_date = '{date}'
    ORDER BY event_date DESC
    LIMIT 1
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
    game_id,
    last_update
    {', format_id' if game.HasFormats else ''}
    )
    VALUES
    ('{event_date}',
    {discord_id},
    {game.ID},
    0
    {f' , {format.ID}' if game.HasFormats else ''}
    )
    RETURNING *
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
      fullparticipants fp
      LEFT JOIN uniquearchetypes ua ON ua.event_id = fp.event_id
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
    