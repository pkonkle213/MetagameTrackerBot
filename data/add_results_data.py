from settings import DATABASE_URL
import psycopg
from tuple_conversions import Standing

#TODO: Why am is this not receiving a Pairing object?
def InsertPairing(
  event_id: int,
  p1name: str,
  p1wins: int,
  p2name: str,
  p2wins: int,
  round_number: int,
  submitter_id: int
) -> int | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    try:
      command = '''
      INSERT INTO pairings
      (event_id,
      round_number,
      player1_game_wins,
      player2_game_wins,
      player1_name,
      player2_name,
      submitter_id)
      VALUES (%s,
      %s,
      %s,
      %s,
      %s,
      %s,
      %s)
      RETURNING event_id
      '''

      criteria = [
        event_id,
        round_number,
        p1wins,
        p2wins,
        p1name,
        p2name,
        submitter_id
      ]
      cur.execute(command, criteria)
      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg.errors.UniqueViolation:
      return None


def CheckPairings(
  event_id: int,
  round_number: int,
  p1name: str,
  p2name: str
) -> bool:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      *
    FROM
      pairings
    WHERE
      event_id = %s
      AND round_number = %s
      AND (
        UPPER(player1_name) = UPPER(%s)
        OR UPPER(player1_name) = UPPER(%s)
        OR UPPER(player2_name) = UPPER(%s)
        OR UPPER(player2_name) = UPPER(%s)
      )
    '''

    criteria = [event_id, round_number, p1name, p2name, p2name, p1name]
    cur.execute(command, criteria)
    row = cur.fetchone()
    return row is None
    

def InsertStanding(
  event_id:int,
  player:Standing,
  submitter_id:int
) -> int | None:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    try:
      command = '''
      INSERT INTO standings
      (event_id,
      player_name,
      wins,
      losses,
      draws,
      submitter_id)
      VALUES
      (%s,
      %s,
      %s,
      %s,
      %s,
      %s)
      RETURNING event_id
      '''

      criteria = [
        event_id,
        player.player_name,
        player.wins,
        player.losses,
        player.draws,
        submitter_id
      ]
      cur.execute(command, criteria)

      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg.errors.UniqueViolation:
      return None
