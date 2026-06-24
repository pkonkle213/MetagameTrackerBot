from psycopg.rows import class_row
from tuple_conversions import Pairing
import psycopg
from settings import DATABASE_URL

def GetEventByRounds(event_id:int) -> list[Pairing]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Pairing)) as cur:
    command = f'''
    SELECT
      round_number,
      player1_name,
      player2_name,
      player1_game_wins,
      player2_game_wins
    FROM
      pairings
    WHERE
      event_id = {event_id}
    ORDER BY
      round_number DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows