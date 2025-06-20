import os
import psycopg2

def GetStoresByPaymentLevel():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT discord_id
    FROM Stores
    WHERE payment_level = 2
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows