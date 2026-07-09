import settings
from tuple_conversions import Store, Game, Format, HubInvite
from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from psycopg.rows import class_row
from typing import NamedTuple
from settings import DATAGUILDID


def GetAllHubInvites(store: Store, format: Format) -> list[HubInvite]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(HubInvite)) as cur:
    command = f"""
    (
      SELECT
        h.hub_name,
        h.invite
      FROM
        hubs_view h
      WHERE
        h.discord_id = {DATAGUILDID}
    )
    UNION ALL
    (
      SELECT
        h.hub_name,
        h.invite
      FROM
        hubs_view h
        INNER JOIN format_channel_maps fcm ON fcm.discord_id = h.discord_id
      WHERE
        h.region_id = {store.region_id}
        AND fcm.format_id = {format.id}
    )
    UNION ALL
    (
      SELECT
        h.hub_name,
        h.invite
      FROM
        hubs_view h
        INNER JOIN region_channel_maps rcm ON rcm.discord_id = h.discord_id
      WHERE
        rcm.region_id = {store.region_id}
        AND h.format_lock = {format.id}
    )
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows
