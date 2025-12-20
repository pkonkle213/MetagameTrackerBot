from data.interaction_data import GetStoreByDiscord
from models.store import Store
from settings import DATABASE_URL
import psycopg2

def UpdateStore(discord_id:int,
  owner_name:str,
  store_name:str, 
  store_address:str, 
  melee_id:str, 
  melee_secret:str) -> Store | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE Stores
    SET store_name = %s
      , owner_name = %s
      , store_address = %s
      {', melee_id = %s' if melee_id else ''}
      {', melee_secret = %s' if melee_secret else ''}
    WHERE discord_id = {discord_id}
    RETURNING discord_id
    '''

    criteria = [store_name, owner_name, store_address]
    if melee_id:
      criteria.append(melee_id)
    if melee_secret:
      criteria.append(melee_secret)
      
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return GetStoreByDiscord(row[0]) if row else None

def DeleteStore(discord_id:int) -> bool:
  conn = psycopg2.connect(DATABASE_URL)
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

def AddStore(discord_id:int,
  discord_name:str,
  owner_id:int,
  owner_name:str) -> Store | None:
  conn = psycopg2.connect(DATABASE_URL)
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
    return GetStoreByDiscord(row[0]) if row else None

def GetAllStoreDiscordIds() -> list[int] | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = '''
    SELECT discord_id
    FROM Stores
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [row[0] for row in rows] if rows else None

def GetClaimFeed(discord_id:int, category_id:int) -> int | None:
  conn = psycopg2.connect(DATABASE_URL)
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

def GetPaidStoreIds() -> list[int] | None:
  conn = psycopg2.connect(DATABASE_URL)
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
    return [row[0] for row in rows] if rows else None