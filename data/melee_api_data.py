from typing import NamedTuple
import psycopg
from psycopg.rows import class_row
from settings import DATABASE_URL

class Details(NamedTuple):
  ClientId: str
  ClientSecret: str

def GetStoreMeleeInfo(store) -> Details | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Details)) as cur:
    command =  f'''
    SELECT
      melee_client_id,
      melee_client_secret
    FROM
      stores
    WHERE
      discord_id = {store.DiscordId}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row