import os
import psycopg2
from tuple_conversions import ConvertToGame, ConvertToFormat, ConvertToStore

def GetFormatByMap(channel_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT f.id, f.name, f.last_ban_update, f.is_limited
    FROM formatchannelmaps fc
    INNER JOIN formats f ON f.id = fc.format_id
    WHERE channel_id = {channel_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return ConvertToFormat(row) if row else None

def GetStoreByDiscord(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      discord_id,
      discord_name,
      store_name,
      owner_id,
      owner_name,
      used_for_data,
      CASE
        WHEN last_payment >= CURRENT_DATE - INTERVAL '1 month' THEN TRUE
        ELSE FALSE
      END AS isPaid
    FROM
      Stores
    WHERE
      discord_id = {discord_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return ConvertToStore(row) if row else None

def GetGameByMap(category_id:int):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT id, name, hasformats
    FROM cardgames g
    INNER JOIN gamecategorymaps gc ON g.id = gc.game_id
    WHERE category_id = {category_id}
    '''
    
    cur.execute(command)
    row = cur.fetchone()
    return ConvertToGame(row) if row else None