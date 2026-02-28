from settings import FIVE6STOREID, DATABASE_URL
import psycopg

def GetFive6Users() -> list[int]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT DISTINCT submitter_id
    FROM player_names
    WHERE discord_id = {FIVE6STOREID}
    '''

    cur.execute(command)
    results = cur.fetchall()
    return [result[0] for result in results]