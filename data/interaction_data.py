from typing import Tuple
from psycopg.rows import class_row
from custom_errors import KnownError
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Format, Game, Store, Hub, Region

def GetHub(discord_id: int) -> Hub | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Hub)) as cur:
    command = f'''
    SELECT
      *
    FROM
      hubs_view
    WHERE
      discord_id = {discord_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row

def GetRegion(discord_id: int, channel_id: int) -> Region | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Region)) as cur:
    command = f'''
    SELECT
      r.id,
      r.region_name
    FROM
      regions r
      INNER JOIN region_channel_maps hc ON hc.region_id = r.id
    WHERE
      hc.discord_id = {discord_id}
      AND hc.channel_id = {channel_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row

def GetGameByHub(category_id: int, hub_discord_id: int) -> Game | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Game)) as cur:
    command = f"""
    (
      SELECT
        g.id,
        g.game_name
      FROM
        games g
        INNER JOIN game_category_maps gc ON g.id = gc.game_id
      WHERE
        gc.category_id = {category_id}
    )
    UNION ALL
    (
      SELECT
        g.id,
        g.game_name
      FROM
        games g
        INNER JOIN hubs_view hv ON hv.game_lock = g.id
      WHERE
        hv.discord_id = {hub_discord_id}
    )
    """
    
    cur.execute(command)
    row = cur.fetchone()
    return row

def GetFormatByHub(channel_id: int, hub_discord_id: int) -> Format | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Format)) as cur:
    command = f"""
    (
      SELECT
        f.id,
        f.format_name,
        f.last_ban_update,
        f.is_limited
      FROM
        format_channel_maps fc
        INNER JOIN formats f ON f.id = fc.format_id
      WHERE
        fc.channel_id = {channel_id}
    )
    UNION ALL
    (
      SELECT
        f.id,
        f.format_name,
        f.last_ban_update,
        f.is_limited
      FROM
        formats f
        INNER JOIN hubs_view hv ON hv.format_lock = f.id
      WHERE
        hv.discord_id = {hub_discord_id}
    )
    """
    cur.execute(command)
    row = cur.fetchone()
    return row

def GetFormatByMap(channel_id: int, hub_discord_id:int) -> Format | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Format)) as cur:
    command = f"""
    (
    SELECT
      f.id,
      f.format_name,
      f.last_ban_update,
      f.is_limited
    FROM
      format_channel_maps fc
      INNER JOIN formats f ON f.id = fc.format_id
    WHERE
      fc.channel_id = {channel_id}
    )
    UNION ALL
    (
      SELECT
        f.id,
        f.format_name,
        f.last_ban_update,
        f.is_limited
      FROM
        formats f
        INNER JOIN hubs_view hv ON hv.format_lock = f.id
      WHERE
        hv.discord_id = {hub_discord_id}
    )
    """
    cur.execute(command)
    row = cur.fetchone()
    return row


def GetStoreByDiscord(discord_id: int) -> Store | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Store)) as cur:
    command = f'''
    SELECT
      discord_id,
      discord_name,
      store_name,
      owner_id,
      owner_name,
      store_address,
      used_for_data,
      region_id,
      is_paid
    FROM
      stores_view
    WHERE
      discord_id = {discord_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row

def GetHubByDiscord(discord_id: int) -> Hub | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Hub)) as cur:
    command = f'''
    SELECT
      discord_id,
      discord_name,
      hub_name,
      owner_id,
      owner_name,
      region_id,
      game_lock,
      format_lock,
      is_paid,
      invite
    FROM
      hubs_view      
    WHERE
      discord_id = {discord_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row

def GetGameByMap(category_id: int, hub_discord_id: int) -> Game | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Game)) as cur:
    command = f"""
    (
      SELECT
        id,
        game_name
      FROM
        games g
        INNER JOIN game_category_maps gc ON g.id = gc.game_id
      WHERE
        gc.category_id = {category_id}
    )
    UNION ALL
    (
      SELECT
        g.id,
        g.game_name
      FROM
        games g
        INNER JOIN hubs_view hv ON hv.game_lock = g.id
      WHERE
        hv.discord_id = {hub_discord_id}
    )
    """

    cur.execute(command)
    row = cur.fetchone()
    return row
