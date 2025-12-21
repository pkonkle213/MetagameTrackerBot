from typing import Any
from settings import DATABASE_URL
import psycopg2


def SubmitTable(event_id: int, p1name: str, p1wins: int, p2name: str,
                p2wins: int, round_number: int,
                submitter_id: int) -> int | None:
  conn = psycopg2.connect(DATABASE_URL)
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
          event_id, round_number, p1wins, p2wins, p1name, p2name, submitter_id
      ]
      cur.execute(command, criteria)
      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None


def AddResult(event_id, player, submitter_id) -> int | None:
  conn = psycopg2.connect(DATABASE_URL)
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
          event_id, player.PlayerName, player.Wins, player.Losses,
          player.Draws, submitter_id
      ]
      cur.execute(command, criteria)

      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None
