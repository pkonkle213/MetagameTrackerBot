from settings import DATABASE_URL
import psycopg2
from tuple_conversions import ConvertToGame, ConvertToFormat, ConvertToStore


#TODO: Why are these in here and not in their corresponding data files?
def GetFormatByMap(channel_id):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT f.id, f.name, f.last_ban_update, f.is_limited
    FROM formatchannelmaps fc
    INNER JOIN formats f ON f.id = fc.format_id
    WHERE fc.channel_id = {channel_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return ConvertToFormat(row) if row else None


def GetStoreByDiscord(discord_id):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
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
    return ConvertToStore(row) if row else None


def GetGameByMap(category_id: int):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT id, name
    FROM Games g
    INNER JOIN gamecategorymaps gc ON g.id = gc.game_id
    WHERE gc.category_id = {category_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return ConvertToGame(row) if row else None
