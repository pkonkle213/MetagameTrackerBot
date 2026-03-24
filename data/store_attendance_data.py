from datetime import date
from settings import DATAGUILDID, DATABASE_URL
import psycopg

from tuple_conversions import Format, Game, Store

def GetAttendance(
  store:Store,
  game:Game,
  format:Format | None,
  start_date:date,
  end_date:date
):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(e.event_date, 'MM/DD') as event_date,
      {'s.store_name,' if store.discord_id == DATAGUILDID else ''}
      {'f.format_name,' if not format else ''}
      e.event_name,
      COUNT(*)
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN Stores s ON s.discord_id = e.discord_id
      INNER JOIN Formats f ON f.id = e.format_id
    WHERE
      e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game.id}
      {f'AND e.format_id = {format.id}' if format else ''}
      AND s.used_for_data = TRUE
      {f'AND e.discord_id = {store.discord_id}' if store.discord_id != DATAGUILDID else ''}
    GROUP BY
      {'e.format_id,' if not format else ''}
      {'s.store_name,' if store.discord_id == DATAGUILDID else ''}
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