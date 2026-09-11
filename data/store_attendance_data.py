from datetime import date
from typing import Any
from settings import DATAGUILDID, DATABASE_URL
import psycopg
from tuple_conversions import Format, Game, Store, Region, Hub

#TODO: This needs to work for format-hubs, region-hubs AND stores
def GetAttendance(
  discord_id: int,
  category_id: int,
  channel_id: int,
  start_date: date,
  end_date: date
) -> list[Any]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      TO_CHAR(e.event_date, 'MM/DD') AS event_date,
      f.format_name,
      e.event_name,
      COUNT(*)
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id AND f.game_id = g.id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      LEFT JOIN game_category_maps gcm ON gcm.discord_id = s.discord_id
      AND gcm.game_id = e.game_id
      LEFT JOIN format_channel_maps fcm ON fcm.discord_id = s.discord_id
      AND fcm.format_id = e.format_id
    WHERE
      e.event_date BETWEEN '%s' AND '%s'
      AND e.discord_id = %s
      AND gcm.category_id = %s        
      AND fcm.channel_id = %s        
    GROUP BY
      e.event_date,
      f.format_name,
      e.event_name
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command, [start_date, end_date, discord_id, category_id, channel_id])
    rows = cur.fetchall()
    return rows