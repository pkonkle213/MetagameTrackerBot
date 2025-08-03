import os
import psycopg2

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

def RegisterStore(discord_id,
  discord_name,
  store_name,
  owner_id,
  owner_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Stores (store_name, discord_id, discord_name, owner_id, owner_name, isApproved, used_for_data, payment_level)
    VALUES (%s, {discord_id}, '{discord_name}', {owner_id}, '{owner_name}', {True}, {True},0)
    RETURNING discord_id, discord_name, store_name, owner_id, owner_name, isApproved, used_for_data, payment_level;
    '''
    
    cur.execute(command, [store_name])
    conn.commit()
    row = cur.fetchone()
    return row

def SetStoreTrackingStatus(approval_status,
   store_discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE Stores
    SET isApproved = {approval_status}
    WHERE discord_id = {store_discord_id}
    RETURNING *
    '''
    
    criteria = (approval_status, store_discord_id)
    cur.execute(command, criteria)
    conn.commit()
    store = cur.fetchone()
    return store
