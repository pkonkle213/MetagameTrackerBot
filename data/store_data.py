import os
import psycopg2

def DeleteStore(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    DELETE FROM Stores
    WHERE discord_id = {discord_id}
    RETURNING TRUE
    '''
    cur.execute(command)
    conn.commit()
    success = cur.fetchone()
    return success

def RegisterStore(discord_id,
  discord_name,
  store_name,
  owner_id,
  owner_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Stores (store_name, discord_id, discord_name, owner_id, owner_name, isApproved, used_for_data, payment_level)
    VALUES (%s, {discord_id}, '{discord_name}', {owner_id}, '{owner_name}', {True}, {True},0)
    RETURNING discord_id, discord_name, store_name, owner_id, owner_name, isApproved, used_for_data, payment_level;
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

def GetStoreParticipantData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      g.name AS Game_Name,
      f.name AS Format_name,
      e.event_date,
      fp.player_name,
      COALESCE(ua.archetype_played, 'UNKNOWN') AS archetype_played,
      fp.wins,
      fp.losses,
      fp.draws
    FROM
      fullparticipants fp
      LEFT JOIN uniquearchetypes ua ON fp.event_id = ua.event_id
      AND fp.player_name = ua.player_name
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN cardgames g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      e.discord_id = {store.DiscordId}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      event_date DESC,
      game_name,
      format_name,
      wins desc,
      draws desc
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetStoreRoundData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      g.name AS Game_Name,
      f.name AS Format_name,
      e.event_date,
      frr.round_number,
      frr.player_name,
      frr.player_archetype,
      frr.opponent_name,
      frr.opponent_archetype,
      frr.result
    FROM
      fullroundresults frr
      INNER JOIN events e ON e.id = frr.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN cardgames g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
    WHERE
      s.discord_id = {store.DiscordId}  
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      g.name,
      f.name,
      e.event_date DESC,
      round_number,
      player_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows