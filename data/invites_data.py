from tuple_conversions import Store, Game, Format
from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from psycopg.rows import class_row
from typing import NamedTuple

class HubInvites(NamedTuple):
  hub_name:str
  invite:str
  
def GetAllHubInvites(
  store:Store,
  game:Game,
  format:Format
) -> list[HubInvites]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(HubInvites)) as cur:
    command = f'''
    SELECT
      hub_name,
      invite
    FROM
      hubs
    WHERE
      invite IS NOT NULL
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    if not rows or len(rows) == 0:
      raise KnownError('No hub invites found')
    return rows
