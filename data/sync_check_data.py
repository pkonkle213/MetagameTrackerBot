from psycopg.rows import scalar_row
from settings import FIVE6STOREID, DATABASE_URL
import psycopg

def GetFive6Users() -> list[int]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    SELECT DISTINCT submitter_id
    FROM player_names
    WHERE discord_id = {FIVE6STOREID}
    '''

    cur.execute(command)
    results = cur.fetchall()
    return results

def GetStores(paid:bool = False) -> list[int]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    SELECT
      discord_id
    FROM
      stores_view
    {f'WHERE is_paid = true' if paid else ''}
    '''

    cur.execute(command)
    results = cur.fetchall()
    return results

def GetHubs(paid:bool = False) -> list[int]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    SELECT
      discord_id
    FROM
      hubs_view
    {f'WHERE is_paid = true' if paid else ''}
    '''

    cur.execute(command)
    results = cur.fetchall()
    return results