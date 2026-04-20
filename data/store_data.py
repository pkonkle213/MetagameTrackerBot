from psycopg.rows import class_row, scalar_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Store

def UpdateStore(
  discord_id:int,
  owner_name:str,
  store_name:str,
  store_address:str,
  melee_id:str | None,
  melee_secret:str | None
) -> Store:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Store)) as cur:
    command = f'''
    UPDATE Stores
    SET store_name = %s
      , owner_name = %s
      , store_address = %s
      {', melee_id = %s' if melee_id else ''}
      {', melee_secret = %s' if melee_secret else ''}
    WHERE discord_id = {discord_id}
    RETURNING discord_id, discord_name, store_name, owner_id, owner_name, store_address, used_for_data, FALSE, is_data_hub
    '''

    criteria = [store_name, owner_name, store_address]
    if melee_id:
      criteria.append(melee_id)
    if melee_secret:
      criteria.append(melee_secret)
      
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    if not row:
      raise Exception(f'Unable to update store: {discord_id}')
    return row

def DeleteStore(discord_id:int) -> bool:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM Stores
    WHERE discord_id = {discord_id}
    RETURNING TRUE
    '''
    cur.execute(command)
    conn.commit()
    success = cur.fetchone()
    return True if success else False

def AddDiscord(
  discord_id:int,
  discord_name:str,
  owner_id:int,
  owner_name:str
) -> int | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = '''
    INSERT INTO discords (discord_id, discord_name, owner_id, owner_name)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (discord_id) DO UPDATE
    SET discord_name = %s, owner_id = %s, owner_name = %s
    RETURNING discord_id
    '''

    criteria = [discord_id, discord_name, owner_id, owner_name]
    cur.execute(command, criteria + criteria[1:])
    conn.commit()
    row = cur.fetchone()
    if not row:
      raise Exception(f'Unable to add discord: {discord_id}')
    return row

def AddStore(discord_id:int) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    INSERT INTO stores (discord_id, used_for_data)
    VALUES (%s, TRUE)
    RETURNING discord_id
    '''

    cur.execute(command, [discord_id])
    conn.commit()
    row = cur.fetchone()
    if not row:
      raise Exception(f'Unable to add store: {discord_id}')
    return row

def GetArchetypeFeed(
  discord_id: int,
  category_id: int
) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    SELECT
      channel_id
    FROM
      archetype_feeds cc
      INNER JOIN game_category_maps gcm ON cc.discord_id = gcm.discord_id
      AND cc.game_id = gcm.game_id
    WHERE
      cc.discord_id = {discord_id}
      AND gcm.category_id = {category_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    if not row:
      raise Exception(f'Unable to find archetype submission feed for store: {discord_id}')
    return row
