import os
import psycopg2

def RegisterStore(discord_id,
  discord_name,
  store_name,
  owner_id,
  owner_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Stores (store_name, discord_id, discord_name, owner_id, owner_name, isApproved, used_for_data)
    VALUES (%s, {discord_id}, '{discord_name}', {owner_id}, '{owner_name}', {False}, {True})
    RETURNING *
    '''
    
    cur.execute(command, [store_name])
    conn.commit()
    row = cur.fetchone()
    return row

def SetStoreTrackingStatus(approval_status,
   store_discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE Stores
    SET isApproved = {approval_status}
    WHERE discord_id = {store_discord_id}
    RETURNING *
    '''
    
    criteria = (approval_status, store_discord_id)
    cur.execute(command, criteria)
    conn.commit()
    store = cur.fetchone()
    return store

def GetStoreData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      c.name AS Game_Name,
      f.name AS Format_Name,
      e.event_date AS Event_Date,
      p.player_name AS Player_Name,
      COALESCE(asu.archetype_played, 'UNKNOWN') AS Archetype_Played,
      p.wins AS Wins,
      p.losses AS Losses,
      p.draws AS Draws
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
              rounddetails rd
              INNER JOIN events e ON e.id = rd.event_id
            WHERE
              e.discord_id = 1210746744602890310
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
              rounddetails rd
              INNER JOIN events e ON e.id = rd.event_id
            WHERE
              e.discord_id = 1210746744602890310
              AND player2_name != 'BYE'
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
          participants p
          INNER JOIN events e ON e.id = p.event_id
        WHERE
          e.discord_id = 1210746744602890310
      ) p
      INNER JOIN events e ON e.id = p.event_id
      INNER JOIN cardgames c ON c.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      LEFT JOIN (
        SELECT DISTINCT
          ON (event_id, player_name) event_id,
          player_name,
          archetype_played
        FROM
          ArchetypeSubmissions
        WHERE
          reported = FALSE
        ORDER BY
          event_id,
          player_name,
          id DESC
      ) asu ON (
        asu.player_name = p.player_name
        AND asu.event_id = p.event_id
      )
    WHERE e.discord_id = {store.DiscordId}
          {f'AND e.game_id = {game.ID}' if game else ''}
          {f'AND e.format_id = {format.ID}' if format else ''}
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      game_name,
      format_name,
      event_date DESC,
      wins desc,
      draws desc
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows