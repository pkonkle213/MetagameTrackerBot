from custom_errors import KnownError
from psycopg.rows import scalar_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Store

def UpdatePlayerNames(store:Store, old_name:str, new_name:str) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    UPDATE pairings
    SET player1_name = CASE WHEN upper(player1_name) = upper('{old_name}') THEN '{new_name}' ELSE player1_name END,
        player2_name = CASE WHEN upper(player2_name) = upper('{old_name}') THEN '{new_name}' ELSE player2_name END
    WHERE event_id IN (
        SELECT id FROM events WHERE discord_id = {store.discord_id}
    )
        AND (UPPER(player1_name) = upper('{old_name}') OR upper(player2_name) = upper('{old_name}'))
    '''

    try:
      cur.execute(command)
      conn.commit()
    except psycopg.errors.UniqueViolation as e:
      raise KnownError(f'Unable to update player names: {e}')