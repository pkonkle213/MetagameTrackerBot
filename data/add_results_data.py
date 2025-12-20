from typing import Any
from models.pairing import Pairing
from settings import DATABASE_URL
import psycopg2
from models.standing import Standing

def SubmitTable(event_id:int,
                players:Pairing,
                submitter_id:int) -> tuple[Any,...] | None:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = '''
    INSERT INTO pairings
    (event_id,
    round_number,
    player1_name,
    player1_game_wins,
    player2_name,
    player2_game_wins,
    submitter_id)
    VALUES (%s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s)
    RETURNING *
    '''

    criteria = [event_id,
    players.RoundNumber,
    players.P1Name,
    players.P1Wins,
    players.P2Name,
    players.P2Wins,
    submitter_id]
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return row if row else None

def AddResult(event_id:int,
              player:Standing,
              submitter_id:int) -> tuple[Any,...] | None:
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
      RETURNING *
      '''

      criteria = [event_id,
                  player.PlayerName,
                  player.Wins,
                  player.Losses,
                  player.Draws,
                  submitter_id]
      cur.execute(command, criteria)
      
      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None