from psycopg.rows import class_row
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

def DeleteStore(discord_id) -> bool:
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

def AddStore(discord_id,
  discord_name,
  owner_id,
  owner_name) -> int:
  conn = psycopg.connect(DATABASE_URL)
  discord_name = discord_name.replace("'","")
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Stores (discord_id, discord_name, owner_id, owner_name, used_for_data, is_data_hub)
    VALUES ({discord_id}, '{discord_name}', {owner_id}, '{owner_name}', {True}, {False})
    ON CONFLICT (discord_id) DO UPDATE
    SET discord_name = '{discord_name}', owner_id = {owner_id}, owner_name = '{owner_name}'
    RETURNING discord_id
    '''

    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    if not row:
      raise Exception(f'Unable to add store: {discord_id}')
    return row[0] 

def GetAllStoreDiscordIds():
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = '''
    SELECT discord_id
    FROM Stores
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [row[0] for row in rows]

def GetClaimFeed(discord_id, category_id):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      channel_id
    FROM
      claimchannels cc
      INNER JOIN gamecategorymaps gcm ON cc.discord_id = gcm.discord_id
      AND cc.game_id = gcm.game_id
    WHERE
      cc.discord_id = {discord_id}
      AND gcm.category_id = {category_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row[0] if row else None

def GetPaidStoreIds():
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      discord_id
    FROM
      stores_view
    WHERE
      isPaid = TRUE
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [row[0] for row in rows]
    