from typing import NamedTuple
import psycopg
from psycopg.rows import class_row
from settings import DATABASE_URL
from tuple_conversions import Store

class Details(NamedTuple):
  melee_client_id: str
  melee_client_secret: str

def GetStoreMeleeInfo(store:Store) -> Details | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Details)) as cur:
    command =  f'''
    SELECT
      melee_client_id,
      melee_client_secret
    FROM
      stores
    WHERE
      discord_id = {store.discord_id}
    '''

    cur.execute(command)
    row = cur.fetchone()
    return row