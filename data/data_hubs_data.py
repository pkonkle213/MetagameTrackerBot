from psycopg.rows import class_row
from tuple_conversions import Store, Event
import psycopg
from settings import DATABASE_URL


def GetHubs(store: Store, event: Event) -> list[Store]:
    """Gets all hubs for a store"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(Store)) as cur:
      command = f"""
      SELECT
        store_name,
        owner_id,
        owner_name,
        store_address,
        used_for_data,
        state,
        region_id,
        is_data_hub,
        hub_format_lock
      FROM
        stores_view sv
      WHERE
        is_data_hub = TRUE
        AND (
          region_id = %s
          OR region_id = 0
        )
        AND (
          hub_format_lock = %s
          OR hub_format_lock = 0
        )
      """

      criteria = [store.region_id, event.format_id]
      cur.execute(command, criteria)
      rows = cur.fetchall()
      if len(rows) == 0:
          raise Exception("No hubs found")
      return rows


def GetChannelGeneralHub(hub: Store, event: Event) -> int:
    """Gets the discordIds and channelIds for general hubs"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(int)) as cur:
      command = f"""
      SELECT
        channel_id
      FROM
        format_channel_maps fcm
        INNER JOIN stores s ON s.discord_id = fcm.discord_id
      WHERE
        s.discord_id = %s
        AND fcm.format_id = %s
      """

      criteria = [hub.discord_id, event.format_id]
      cur.execute(command, criteria)
      row = cur.fetchone()
      if not row:
        raise Exception("No channels found for hub")
      return row


def GetChannelFormatLocked(hub: Store, store: Store) -> int:
    """Gets the channel id for the format of the event"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(int)) as cur:
      command = f"""
      SELECT
        channel_id
      FROM
        region_channel_maps rcm
        INNER JOIN stores s ON s.discord_id = rcm.discord_id
      WHERE
        s.discord_id = %s
        AND rcm.region_id = %s
      """

      criteria = [hub.discord_id, store.region_id]
      cur.execute(command, criteria)
      row = cur.fetchone()
      if not row:
        raise Exception("No channel found for region")
      return row
