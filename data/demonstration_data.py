import os
import psycopg2

def UpdateDemo(event_id, event_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET event_date = '{event_date}'
    WHERE id = {event_id}
    '''
    
    cur.execute(command)
    conn.commit()

def DeleteDemo():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'DELETE FROM Events WHERE discord_id = 1357401531435192431 and id > 12;'
    cur.execute(command)
    conn.commit()