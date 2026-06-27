from custom_errors import KnownError
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Region, Hub
from psycopg.rows import class_row

def GetRegions(hub:Hub) -> list[Region]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Region)) as cur:
    command = f"""
    SELECT
      id,
      region_name
    FROM
      regions
    ORDER BY region_name
    """
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def AddRegionMap(hub:Hub,
                 channel_id: int,
                 region:Region) -> tuple[int, int, int]:
   conn = psycopg.connect(DATABASE_URL)
   with conn, conn.cursor() as cur:
      command = f"""
      INSERT INTO region_channel_maps (discord_id, channel_id, region_id)
      VALUES ({hub.discord_id}, {channel_id}, {region.id})
      ON CONFLICT (discord_id, channel_id) DO UPDATE
      SET region_id = {region.id}
      RETURNING *
      """
      cur.execute(command)
      conn.commit()
      row = cur.fetchone()
      if not row:
         raise KnownError('Failed to map region. Please try again later.')
      return row