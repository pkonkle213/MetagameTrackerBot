import os
import psycopg2

from tuple_conversions import ConvertToStore, Store

def UpdateStore(discord_id
                , owner_name
                , store_name
                , store_address
                , melee_id
                , melee_secret
               ) -> Store | None:
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE Stores
    SET store_name = %s
      , owner_name = %s
      , store_address = %s
      , melee_id = %s
      , melee_secret = %s
    WHERE discord_id = {discord_id}
    RETURNING discord_id, discord_name, store_name, owner_id, owner_name, used_for_data, FALSE
    '''
    cur.execute(command,
                [store_name
                 , owner_name
                 , store_address
                 , melee_id
                 , melee_secret])
    conn.commit()
    row = cur.fetchone()
    return ConvertToStore(row) if row else None

def DeleteStore(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM Stores
    WHERE discord_id = {discord_id}
    RETURNING TRUE
    '''
    cur.execute(command)
    conn.commit()
    success = cur.fetchone()
    return success

def AddStore(discord_id,
  discord_name,
  owner_id,
  owner_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Stores (discord_id, discord_name, owner_id, owner_name, used_for_data)
    VALUES ({discord_id}, '{discord_name}', {owner_id}, '{owner_name}', {True})
    ON CONFLICT (discord_id) DO UPDATE
    SET discord_name = '{discord_name}', owner_id = {owner_id}, owner_name = '{owner_name}'
    RETURNING discord_id, discord_name, 'NONE', owner_id, owner_name, used_for_data, FALSE
    '''

    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return ConvertToStore(row) if row else None

#This needs to update the store profile
#Store name, store address, lpayout style
def RegisterStore(discord_id,
  discord_name,
  store_name,
  owner_id,
  owner_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Stores (store_name, discord_id, discord_name, owner_id, owner_name, used_for_data)
    VALUES (%s, {discord_id}, '{discord_name}', {owner_id}, '{owner_name}', {True})
    RETURNING discord_id, discord_name, store_name, owner_id, owner_name, used_for_data, FALSE
    '''
    
    cur.execute(command, [store_name])
    conn.commit()
    row = cur.fetchone()
    return ConvertToStore(row) if row else None

def GetAllStoreDiscordIds():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT discord_id
    FROM Stores
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [row[0] for row in rows]

def GetClaimFeed(discord_id, category_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
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