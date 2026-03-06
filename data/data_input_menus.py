from typing import Tuple
from psycopg.rows import class_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Event, Format, Game, Store

def GetPreviousEvents(
  store:Store,
  game:Game,
  format:Format,
  event_type:int = 0,
  interval:int=2,
  archetypes=False
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
      e.reported_as
    FROM
      events_view e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      s.discord_id = {store.DiscordId}
      AND e.game_id = {game.GameId}
      AND e.format_id = {format.FormatId}
      AND e.event_date >= CURRENT_DATE - INTERVAL '{interval} weeks'
      {f'AND e.event_type_id = {event_type}' if event_type else ''}
    ORDER BY
      {'e.event_date DESC' if archetypes or event_type else 'e.created_at DESC'}
    LIMIT 24
    '''

    cur.execute(command)  # type: ignore[arg-type]
    rows = cur.fetchall()
    
    return rows

def GetEventTypes() -> list[Tuple[int, str]]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
       id,  
       event_type
    FROM
      event_types
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows