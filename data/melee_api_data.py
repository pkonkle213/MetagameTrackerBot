import psycopg2
import os
from collections import namedtuple

def GetStoreMeleeInfo(store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      melee_client_id,
      melee_client_secret
    FROM
      stores
    WHERE
      discord_id = {store.DiscordId}
    '''

    Details = namedtuple('ApiDetail',
                         ['ClientId',
                          'ClientSecret']
                        )
    cur.execute(command)
    row = cur.fetchone()
    return Details(row[0],row[1]) if row else Details(None, None)