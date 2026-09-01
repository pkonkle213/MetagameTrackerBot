from custom_errors import KnownError
from psycopg.rows import class_row, scalar_row
from tuple_conversions import Store, Event, HubsChannels, Game, Format, Hub
import psycopg
from settings import DATABASE_URL

def GetPossibleHubs(
  store:Store,
  game:Game | None,
  format:Format | None
) -> list[Hub]:
  """Gets all hubs related to a store, game, and format"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Hub)) as cur:
    command = f"""
    (
      SELECT
        hv.discord_id,
        hv.discord_name,
        hv.hub_name,
        hv.owner_id,
        hv.owner_name,
        hv.region_id,
        hv.game_lock,
        hv.format_lock,
        hv.is_paid,
        hv.invite
      FROM
        stores s
        INNER JOIN hubs_view hv ON hv.region_id = s.region_id
        INNER JOIN format_channel_maps fcm ON fcm.discord_id = hv.discord_id
      WHERE
        s.discord_id = {store.discord_id}
        {f"AND fcm.format_id = {format.id}" if format else ""}
    )
    UNION
    (
      SELECT
        hv.discord_id,
        hv.discord_name,
        hv.hub_name,
        hv.owner_id,
        hv.owner_name,
        hv.region_id,
        hv.game_lock,
        hv.format_lock,
        hv.is_paid,
        hv.invite
      FROM
        stores s
        INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
        INNER JOIN hubs_view hv ON rcm.discord_id = hv.discord_id
      WHERE
        s.discord_id = {store.discord_id}
        AND rcm.region_id = {store.region_id}
        {f'AND hv.format_lock = {format.id}' if format else ''}
    )
    LIMIT
      25
    """

    cur.execute(command) #type:ignore[arg-type]
    rows = cur.fetchall()
    return rows

#TODO: How can I simplify this now that I have stores_approved_hubs?
def GetAllHubs(event:Event) -> list[HubsChannels]:
  """Gets all hub discordIds and channelIds for an event"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(HubsChannels)) as cur:
    command = f"""
    (
      --Region Locked Hubs
      SELECT
        hv.discord_id,
        fcm.channel_id
      FROM
        events e
        INNER JOIN stores s ON s.discord_id = e.discord_id
        INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = s.discord_id
        INNER JOIN hubs_view hv ON hv.discord_id = sah.hub_discord_id
        INNER JOIN format_channel_maps fcm ON fcm.format_id = e.format_id
        AND fcm.discord_id = hv.discord_id
      WHERE
        e.id = {event.id}
        AND fcm.format_id = {event.format_id}
    )
    UNION ALL
    (
      --Format Locked Hubs
      SELECT
        hv.discord_id,
        rcm.channel_id
      FROM
        events e
        INNER JOIN stores s ON e.discord_id = s.discord_id
        INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = s.discord_id
        INNER JOIN hubs_view hv ON hv.discord_id = sah.hub_discord_id
        INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
        AND rcm.discord_id = hv.discord_id
      WHERE
        e.id = {event.id}
        AND e.discord_id = {event.discord_id}
    )
    UNION ALL
    (
      --Global Hubs
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

    cur.execute(command) #type:ignore[arg-type]
    rows = cur.fetchall()
    if len(rows) == 0:
      raise Exception("No hubs found")
    return rows
