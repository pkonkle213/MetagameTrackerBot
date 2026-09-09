from settings import DATABASE_URL
from psycopg.rows import class_row
from custom_errors import KnownError
import psycopg
from tuple_conversions import Region, Format, Game, Hub, Store

def GetAllowedStores(hub: Hub, game: Game, format: Format, region: Region) -> list[Store]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Store)) as cur:
    command = f"""
    SELECT
      sv.discord_id
      , sv.discord_name
      , sv.owner_id
      , sv.owner_name
      , sv.store_name
      , sv.store_address
      , sv.used_for_data
      , sv.region_id
      , sv.is_paid
    FROM
      stores_approved_hubs sah
      INNER JOIN stores_view sv ON sv.discord_id = sah.store_discord_id
    WHERE
      sah.hub_discord_id = {hub.discord_id}
      AND sah.region_id = {region.id}
      AND sah.game_id = {game.id}
      AND sah.format_id = {format.id}
    LIMIT 25
    """

    cur.execute(command)
    conn.commit()

    rows = cur.fetchall()
    if len(rows) == 0:
      raise KnownError('No supported stores found')
    return rows

def UpdateAssociatedStores(
  league_id:int,
  selected_store_ids: list[int]
) -> bool:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    delete_command = f"""
    DELETE FROM hub_league_stores
    WHERE league_id = %s
    """

    add_command = f"""
    INSERT INTO hub_league_stores (league_id, store_discord_id)
    SELECT
      %s,
      unnest(%s::bigint[])
    """

    try:
      cur.execute(delete_command, [league_id])
      conn.commit()

      cur.execute(add_command, [league_id, selected_store_ids])
      conn.commit()
      return True
    except Exception as e:
      print('Error:', e)
      return False