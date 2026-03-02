from typing import Tuple
from psycopg.rows import class_row
from custom_errors import KnownError
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Format, Game, Store


#TODO: Why are these in here and not in their corresponding data files?
def GetFormatByMap(channel_id:int) -> Format | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Format)) as cur:
    command = f'''
    SELECT f.id, f.name, f.last_ban_update, f.is_limited
    FROM formatchannelmaps fc
    INNER JOIN formats f ON f.id = fc.format_id
    WHERE fc.channel_id = {channel_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row


def GetStoreByDiscord(discord_id:int) -> Store | None:
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
      isPaid,
      state,
      region,
      is_data_hub
    FROM
      stores_view
    WHERE
      discord_id = {discord_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row


def GetGameByMap(category_id: int) -> Game | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Game)) as cur:
    command = f'''
    SELECT id, name
    FROM Games g
    INNER JOIN gamecategorymaps gc ON g.id = gc.game_id
    WHERE gc.category_id = {category_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row

def GetInteractionDetails(
  discord_id: int,
  category_id: int,
  channel_id: int
) -> Tuple[Store | None, Game | None, Format | None]:
  conn = psycopg.connect(DATABASE_URL)
  with  conn, conn.cursor() as cur:
    command = f'''
    SELECT
      s.discord_id,
      s.discord_name,
      s.store_name,
      s.owner_id,
      s.owner_name,
      s.store_address,
      s.used_for_data,
      s.state,
      s.region,
      s.isPaid,
      s.is_data_hub,
      g.game_id,
      g.game_name,
      f.format_id,
      f.format_name,
      f.last_ban_update,
      f.is_limited
    FROM
      stores_view s
      LEFT JOIN (
        SELECT
          gcm.discord_id,
          g.id AS game_id,
          g.name AS game_name
        FROM
          gamecategorymaps gcm
          INNER JOIN games g ON g.id = gcm.game_id
        WHERE
          gcm.category_id = {category_id}
      ) g ON g.discord_id = s.discord_id
      LEFT JOIN (
        SELECT
          fcm.discord_id,
          f.game_id AS game_id,
          f.id AS format_id,
          f.name AS format_name,
          f.last_ban_update,
          f.is_limited
        FROM
          formatchannelmaps fcm
          INNER JOIN formats f ON f.id = fcm.format_id
        WHERE
          fcm.channel_id = {channel_id}
      ) f ON f.discord_id = s.discord_id
      AND f.game_id = g.game_id
    WHERE
      s.discord_id = {discord_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    if not row:
      raise KnownError('Nothing found for data provided')
    store = Store(*row[0:11]) if row[0] else None
    game = Game(*row[11:13]) if row[11] else None
    format = Format(*row[13:17]) if row[13] else None
    return store, game, format