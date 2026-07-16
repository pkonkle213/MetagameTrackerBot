from psycopg.rows import class_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Event, Format, Game, Store, EventType

def GetPreviousEvents(
  store:Store,
  game:Game,
  format:Format,
  event_type:int = 0,
  interval:int = 2,
  archetypes:bool = False
) -> list[Event]:
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
      e.league_id,
      e.is_complete
    FROM
      events_view e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      s.discord_id = {store.discord_id}
      AND e.game_id = {game.id}
      AND e.format_id = {format.id}
      AND e.event_date >= CURRENT_DATE - INTERVAL '{interval} weeks'
      {f'AND e.event_type_id = {event_type}' if event_type else ''}
    ORDER BY
      {'e.event_date DESC' if archetypes or event_type else 'e.created_at DESC'}
    LIMIT 24
    '''

    cur.execute(command)  # type: ignore[arg-type]
    rows = cur.fetchall()
    
    return rows

def GetEventTypes(
  discord_id: int,
  game: Game,
  format:Format
) -> list[EventType]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(EventType)) as cur:
    command = '''
    (
      SELECT
        - id AS id,
        name
      FROM
        leagues
      WHERE
        end_date >= NOW()
        AND start_date <= NOW()
        AND discord_id = %s
        AND game_id = %s
        AND format_id = %s
      ORDER BY
        end_date DESC,
        start_date DESC
    )
    UNION ALL
    (
      SELECT
        id,
        event_type
      FROM
        event_types
      WHERE
        id NOT IN (3)
      ORDER BY
        id
    )
    LIMIT 25
    '''

    cur.execute(command, [discord_id, game.id, format.id])
    rows = cur.fetchall()
    return rows