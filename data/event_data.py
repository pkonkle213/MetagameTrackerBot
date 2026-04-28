from datetime import date
from typing import Tuple
import psycopg
from psycopg.rows import class_row, scalar_row
from settings import DATABASE_URL
from tuple_conversions import Event, EventInput, Format, Game, Store

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
    , {event.event_type_id if int(event.event_type_id) > 0 else 3}
    , CURRENT_TIMESTAMP AT TIME ZONE 'America/New_York'
    , {user_id}
    {f', {-event.event_type_id}' if int(event.event_type_id) < 0 else ', NULL'}
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

def GetStoreEvents(
  store:Store,
  game:Game,
  format:Format,
):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Event)) as cur:
    command = f'''
    SELECT
      e.id,
      e.custom_event_id,
      e.discord_id,
      e.event_date,
      e.game_id,
      e.format_id,
      e.last_update,
      e.event_name,
      e.event_type_id,
      e.reported_as,
      e.created_by,
      e.created_at,
      e.league_id
    FROM
      events_view e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      s.discord_id = {store.discord_id}
      AND e.game_id = {game.id}
      AND e.format_id = {format.id}
      AND e.event_date >= CURRENT_DATE - INTERVAL '4 weeks'
    ORDER BY
      e.event_date DESC
    LIMIT 25
    '''

    cur.execute(command)  # type: ignore[arg-type]
    rows = cur.fetchall()

    return rows

def GetHubEvents(discord_id: int, channel_id:int) -> list[Event]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Event)) as cur:
    command = f'''
    (
      SELECT
        e.id,
        e.discord_id,
        e.event_date,
        e.game_id,
        e.format_id,
        e.last_update,
        e.event_type_id,
        s.store_name || ' - ' || e.event_name AS event_name,
        e.custom_event_id,
        e.created_at,
        e.created_by,
        e.league_id,
        e.reported_as
      FROM
        events_view e
        INNER JOIN stores_view s ON s.discord_id = e.discord_id
        INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
        INNER JOIN hubs_view h ON h.discord_id = rcm.discord_id
      WHERE
        h.discord_id = {discord_id}
        AND rcm.channel_id = {channel_id}
      ORDER BY
        e.event_date DESC
    )
    UNION ALL
    (
      SELECT
        e.id,
        e.discord_id,
        e.event_date,
        e.game_id,
        e.format_id,
        e.last_update,
        e.event_type_id,
        s.store_name || ' - ' || e.event_name AS event_name,
        e.custom_event_id,
        e.created_at,
        e.created_by,
        e.league_id,
        e.reported_as
      FROM
        events_view e
        INNER JOIN stores_view s ON s.discord_id = e.discord_id
        INNER JOIN format_channel_maps fcm ON fcm.format_id = e.format_id
        INNER JOIN hubs_view h ON h.discord_id = fcm.discord_id
      WHERE
        h.discord_id = {discord_id}
        AND fcm.channel_id = {channel_id}
      ORDER BY
        e.event_date DESC
    )
    LIMIT
      25
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows