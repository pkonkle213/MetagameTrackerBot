import os
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])

#This is only to be used when I need to rebuild the database
def ArchetypeSubmissions():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      id,
      event_id,
      player_name,
      archetype_played,
      date_submitted,
      submitter_id,
      submitter_username,
      reported
    FROM ArchetypeSubmissions
    ORDER BY id
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def BadWords():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      id,
      word
    FROM BadWords
    ORDER BY id
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def BadWordsStoresBridge():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      badword_id,
      discord_id
    FROM BadWords_Stores
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def CardGames():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      id,
      name,
      has_formats
    FROM CardGames
    ORDER BY id
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def ClaimReportChannels():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      discord_id,
      channel_id,
      game_id
    FROM ClaimReportChannels
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def Events():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      id,
      discord_id,
      event_date,
      game_id,
      format_id,
      last_update
    FROM Events
    ORDER BY id
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def FormatChannelMaps():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      discord_id,
      channel_id,
      format_id
    FROM FormatChannelMaps
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def Formats():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      id,
      game_id,
      name,
      last_ban_update,
      is_limited
    FROM Formats
    ORDER BY id
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GameCategoryMaps():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      discord_id,
      category_id,
      game_id
    FROM GameCategoryMaps
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def Participants():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      event_id,
      player_name,
      wins,
      losses,
      draws,
      submitter_id
    FROM Participants
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def RoundDetails():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      event_id,
      round_number,
      player1_name,
      player1_game_wins,
      player2_name,
      player2_game_wins,
      submitter_id
    FROM RoundDetails
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def Stores():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      discord_id,
      discord_name,
      store_name,
      owner_id,
      owner_name,
      used_for_data,
      is_paid
    FROM Stores
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows