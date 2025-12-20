import psycopg2
from models.format import Format
from models.game import Game
from models.store import Store
from settings import DATABASE_URL

#TODO: Why are these in here and not in their corresponding data files?
def GetFormatByMap(channel_id:int) -> Format | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT f.id, f.name, f.last_ban_update, f.is_limited
    FROM formatchannelmaps fc
    INNER JOIN formats f ON f.id = fc.format_id
    WHERE channel_id = {channel_id}
    '''
    cur.execute(command)
    row = cur.fetchone()

    return Format(row[0], row[1], row[2], row[3]) if row else None

def GetStoreByDiscord(discord_id:int) -> Store | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command =  f'''
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
    
    return Store(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) if row else None

def GetGameByMap(category_id:int) -> Game | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT id, name
    FROM Games g
    INNER JOIN gamecategorymaps gc ON g.id = gc.game_id
    WHERE category_id = {category_id}
    '''
    
    cur.execute(command)
    row = cur.fetchone()

    return Game(row[0], row[1]) if row else None