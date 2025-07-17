import os
import psycopg2

def GetEventObj(discord_id,
                date,
                game,
                format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update
    FROM events e
    WHERE e.discord_id = {discord_id}
      AND e.game_id = {game.ID}
      AND e.format_id = {format.ID}
      AND e.event_date = '{date}'
    ORDER BY event_date DESC
    LIMIT 1
    '''
    
    cur.execute(command)
    row = cur.fetchone()
    return row if row else None

def CreateEvent(event_date,
  discord_id,
  game,
  format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events
    (event_date,
    discord_id,
    game_id,
    last_update
    {', format_id' if game.HasFormats else ''}
    )
    VALUES
    ('{event_date}',
    {discord_id},
    {game.ID},
    0
    {f' , {format.ID}' if game.HasFormats else ''}
    )
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    event = cur.fetchone()
    return event if event else None

#TODO: Update this using the full participants view
def GetEventMeta(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      archetype_played,
      wins,
      losses,
      draws
    FROM
      (
        SELECT
          event_id,
          p.player_name,
          COUNT(
            CASE
              WHEN match_result = 'WIN' THEN 1
            END
          ) AS wins,
          COUNT(
            CASE
              WHEN match_result = 'LOSS' THEN 1
            END
          ) AS losses,
          COUNT(
            CASE
              WHEN match_result = 'DRAW' THEN 1
            END
          ) AS draws
        FROM
          (
            SELECT
              event_id,
              player1_name AS player_name,
              CASE
                WHEN player1_game_wins > player2_game_wins THEN 'WIN'
                WHEN player1_game_wins = player2_game_wins THEN 'DRAW'
                ELSE 'LOSS'
              END AS match_result
            FROM
              rounddetails
            WHERE
              event_id = {event_id}
            UNION ALL
            SELECT
              event_id,
              player2_name AS player_name,
              CASE
                WHEN player2_game_wins > player1_game_wins THEN 'WIN'
                WHEN player2_game_wins = player1_game_wins THEN 'DRAW'
                ELSE 'LOSS'
              END AS match_result
            FROM
              rounddetails
            WHERE
              player2_name != 'BYE'
              AND event_id = {event_id}
            ORDER BY
              player_name
          ) p
        GROUP BY
          event_id,
          p.player_name
        UNION ALL
        SELECT
          event_id,
          player_name,
          wins,
          losses,
          draws
        FROM
          participants
        WHERE
          event_id = {event_id}
      ) x
      LEFT JOIN (
        SELECT DISTINCT
          ON (event_id, player_name) event_id,
          player_name,
          archetype_played
        FROM
          ArchetypeSubmissions
        ORDER BY
          event_id,
          player_name,
          id DESC
      ) ap ON ap.event_id = x.event_id
      AND ap.player_name = x.player_name
    ORDER BY wins DESC, draws DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows