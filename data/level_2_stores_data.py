import os
import psycopg2

def GetStoresByPaymentLevel(payment_level:int = 2):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT discord_id
    FROM Stores
    WHERE payment_level = {payment_level}
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows