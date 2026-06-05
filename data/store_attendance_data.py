from datetime import date
from typing import Any
from settings import DATAGUILDID, DATABASE_URL
import psycopg
from tuple_conversions import Format, Game, Store, Region, Hub

def GetHubAttendance(
  hub:Hub,
  region:Region | None,
  game:Game,
  format:Format | None,
  start_date:date,
  end_date:date
) -> list[Any]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(e.event_date, 'MM/DD') as event_date,
      s.store_name,
      {'f.format_name,' if not format else ''}
      e.event_name,
      COUNT(*)
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
    WHERE
      e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game.id}
      {f'AND e.format_id = {format.id}' if format else ''}
      AND {f's.region_id = {region.id}' if region else f'rcm.discord_id = {hub.discord_id}'}
    GROUP BY
      format_id,
      f.format_name,
      e.event_date,
      e.game_id,
      s.store_name,
      e.event_name
    ORDER BY
      e.event_date DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetStoreAttendance(
  store:Store,
  game:Game,
  format:Format | None,
  start_date:date,
  end_date:date
) -> list[Any]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(e.event_date, 'MM/DD') as event_date,
      {'f.format_name,' if not format else ''}
      e.event_name,
      COUNT(*)
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game.id}
      {f'AND e.format_id = {format.id}' if format else ''}
      AND s.discord_id = {store.discord_id}
    GROUP BY
      {'e.format_id,' if not format else ''}
      {'f.format_name,' if not format else ''}
      e.event_date,
      e.game_id,
      e.event_name
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows