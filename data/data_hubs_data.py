from psycopg.rows import class_row, scalar_row
from tuple_conversions import Store, Event, HubsChannels
import psycopg
from settings import DATABASE_URL

def GetAllHubs(event:Event) -> list[HubsChannels]:
  """Gets all hub discordIds and channelIds for an event"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(HubsChannels)) as cur:
    command = f"""
    (
      SELECT
        hv.discord_id,
        fcm.channel_id
      FROM
        events e
        INNER JOIN stores s ON s.discord_id = e.discord_id
        INNER JOIN hubs_view hv ON hv.region_id = s.region_id
        INNER JOIN format_channel_maps fcm ON fcm.format_id = e.format_id
        AND fcm.discord_id = hv.discord_id
      WHERE
        e.id = {event.id}
    )
    UNION ALL
    (
      SELECT
        hv.discord_id,
        rcm.channel_id
      FROM
        events e
        INNER JOIN hubs_view hv ON hv.format_lock = e.format_id
        INNER JOIN stores s ON e.discord_id = s.discord_id
        INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
        AND rcm.discord_id = hv.discord_id
      WHERE
        e.id = {event.id}
    )
    UNION ALL
    (
      SELECT
        hv.discord_id, fcm.channel_id
      FROM
        hubs_view hv
        INNER JOIN format_channel_maps fcm ON fcm.discord_id = hv.discord_id
        INNER JOIN events e ON fcm.format_id = e.format_id
      WHERE
        region_id = 0
        AND e.id = {event.id}
    )
    """

    cur.execute(command)
    rows = cur.fetchall()
    if len(rows) == 0:
      raise Exception("No hubs found")
    return rows
