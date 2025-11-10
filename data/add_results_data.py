import os
import psycopg2

#TODO: The player names should be injected to prevent SQL injection attacks
def SubmitTable(event_id,
                p1name,
                p1wins,
                p2name,
                p2wins,
                round_number,
                submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO pairings
    (event_id,
    round_number,
    player1_game_wins,
    player2_game_wins,
    player1_name,
    player2_name,
    submitter_id)
    VALUES ({event_id},
    {round_number},
    {p1wins},
    {p2wins},
    '{p1name}',
    '{p2name}',
    {submitter_id})
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row if row else None

def AddResult(event_id,
              player,
              submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      #I'm choosing to inject these values due to player_name technically being a string of user input
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
      
      cur.execute(command,
                  (event_id,
                   player.PlayerName,
                   player.Wins,
                   player.Losses,
                   player.Draws,
                   submitter_id)
                 )
      
      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None