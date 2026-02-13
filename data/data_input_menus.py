from settings import DATABASE_URL
import psycopg2
from tuple_conversions import Format, Game, Store

def GetPreviousEvents(store:Store, game:Game, format:Format, interval:int=2):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      e.id,
      TO_CHAR(e.event_date, 'MM/DD') as event_date,
      e.event_name,
      et.event_type
    FROM
      events e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN event_types et ON et.id = e.event_type_id
    WHERE
      s.discord_id = {store.DiscordId}
      AND e.game_id = {game.GameId}
      AND e.format_id = {format.FormatId}
      AND e.event_date >= CURRENT_DATE - INTERVAL '{interval} weeks'
    ORDER BY
      e.id DESC
    LIMIT 25
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetEventTypes():
  conn = psycopg2.connect(DATABASE_URL)
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