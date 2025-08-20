import os
import psycopg2

def GetStoreParticipantData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      g.name AS Game_Name,
      f.name AS Format_Name,
      DATE(e.event_date) as Event_Date,
      fp.Player_Name,
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

def GetPlayerRoundData(store, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      g.name AS Game_Name,
      f.name AS Format_name,
      e.event_date,
      frr.round_number,
      frr.player_archetype as your_archetype,
      frr.opponent_archetype as opponents_archetype,
      frr.result
    FROM
      fullroundresults frr
      INNER JOIN events e ON e.id = frr.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN cardgames g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN playernames pn ON pn.discord_id = e.discord_id
      AND pn.player_name = frr.player_name
    WHERE
      s.discord_id = {store.DiscordId}
      AND pn.submitter_id = {user_id}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY
      g.name,
      f.name,
      e.event_date DESC,
      round_number
    '''

    print('Player participant:', command)
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetPlayerParticipantData(store, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      g.name AS Game_Name,
      f.name AS Format_name,
      e.event_date,
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
      INNER JOIN playernames pn ON pn.discord_id = e.discord_id
      AND pn.player_name = fp.player_name
    WHERE
      e.discord_id = {store.DiscordId}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND pn.submitter_id = {user_id}
    ORDER BY
      event_date DESC,
      game_name,
      format_name,
      wins desc,
      draws desc
    '''

    print('Player round:', command)
    cur.execute(command)
    rows = cur.fetchall()
    return rows
    