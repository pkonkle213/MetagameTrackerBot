import os
import psycopg2

def GetStoreStandingData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      INITCAP(g.name) AS Game_Name,
      INITCAP(f.name) AS Format_Name,
      DATE (e.event_date) AS Event_Date,
      INITCAP(fp.Player_Name) AS player_name,
      INITCAP(COALESCE(ua.archetype_played, 'UNKNOWN')) AS archetype_played,
      fp.wins,
      fp.losses,
      fp.draws
    FROM
      full_standings fp
      LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id
      AND UPPER(fp.player_name) = UPPER(ua.player_name)
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN Games g ON g.id = e.game_id
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

def GetStorePairingData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      INITCAP(g.name) AS Game_Name,
      INITCAP(f.name) AS Format_name,
      e.event_date,
      frr.round_number,
      INITCAP(frr.player_name) as player_name,
      INITCAP(COALESCE(ua1.archetype_played, 'UNKNOWN')) AS player_archetype,
      INITCAP(frr.opponent_name),
      INITCAP(COALESCE(ua2.archetype_played, 'UNKNOWN')) AS opponent_archetype,
      INITCAP(frr.result) as result
    FROM
      full_pairings frr
      INNER JOIN events e ON e.id = frr.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN Games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      LEFT JOIN unique_archetypes ua1 ON ua1.event_id = e.id
      AND upper(ua1.player_name) = upper(frr.player_name)
      LEFT JOIN unique_archetypes ua2 ON ua2.event_id = e.id
      AND upper(ua2.player_name) = upper(frr.opponent_name)
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
      frr.player_name
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetPlayerPairingData(store, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      INITCAP(g.name) AS Game_Name,
      INITCAP(f.name) AS Format_name,
      e.event_date,
      frr.round_number,
      INITCAP(COALESCE(ua1.archetype_played, 'UNKNOWN')) as your_archetype,
      INITCAP(COALESCE(ua2.archetype_played, 'UNKNOWN')) as opponents_archetype,
      INITCAP(frr.result) as result
    FROM
      full_pairings frr
      INNER JOIN events e ON e.id = frr.event_id
      LEFT JOIN unique_archetypes ua1 ON e.id = ua1.event_id AND UPPER(frr.player_name) = UPPER(ua1.player_name)
      LEFT JOIN unique_archetypes ua2 ON e.id = ua2.event_id AND UPPER(frr.opponent_name) = UPPER(ua2.player_name)
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id
      AND UPPER(pn.player_name) = UPPER(frr.player_name)
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

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetPlayerStandingData(store, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT
      INITCAP(g.name) AS Game_Name,
      INITCAP(f.name) AS Format_name,
      e.event_date,
      INITCAP(COALESCE(ua.archetype_played, 'UNKNOWN')) AS archetype_played,
      fp.wins,
      fp.losses,
      fp.draws
    FROM
      full_standings fp
      LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id
      AND fp.player_name = ua.player_name
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id
      AND UPPER(pn.player_name) = UPPER(fp.player_name)
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

    cur.execute(command)
    rows = cur.fetchall()
    return rows
    