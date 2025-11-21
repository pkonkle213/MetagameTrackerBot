import os
import psycopg2
from settings import TESTGUILDID

def UpdateDemo(event_id, event_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET event_date = '{event_date}', discord_id = {TESTGUILDID}
    WHERE id = {event_id}
    '''
    
    cur.execute(command)
    conn.commit()

def DeleteDemo():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'DELETE FROM Events WHERE discord_id = {TESTGUILDID} and id > 12;'
    cur.execute(command)
    conn.commit()