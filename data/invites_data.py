import settings
from tuple_conversions import Store, Game, Format, Hub
from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from psycopg.rows import class_row
from typing import NamedTuple
from settings import DATAGUILDID
  
def GetAllHubInvites(
  store:Store,
  format:Format
) -> list[Hub]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Hub)) as cur:
    command = f'''
    (
      SELECT
        *
      FROM
        hubs_view
      WHERE
        discord_id = {DATAGUILDID}
    )
    UNION ALL
    (
      SELECT
        *
      FROM
        hubs_view hv
        INNER JOIN format_channel_maps fcm ON fcm.discord_id = hv.discord_id
      WHERE
        hv.region_id = {store.region_id}
        AND fcm.format_id = {format.id}
    )
    UNION ALL
    (
      SELECT
        *
      FROM
        hubs_view hv
        INNER JOIN region_channel_maps rcm ON rcm.discord_id = hv.discord_id
      WHERE
        rcm.region_id = {store.region_id}
        AND hv.format_lock = {format.id}
    )
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    if not rows or len(rows) == 0:
      raise KnownError('No hub invites found')
    return rows
