from collections import namedtuple
import os
import psycopg2
from psycopg2.errors import UniqueViolation

def AddWord(word):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  try:
    with conn, conn.cursor() as cur:
      criteria = [word]
      command = '''
      INSERT INTO BadWords (badword)
      VALUES (%s)
      RETURNING *
      '''

      cur.execute(command, criteria)
      conn.commit()
      row = cur.fetchall()
      Word = namedtuple("Word", ["ID", "Word"])
      return Word(row[0], row[1])
  except UniqueViolation:
    return None

def GetWord(word):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT id, badword
    FROM BadWords
    WHERE badword = %s
    '''
    
    criteria = [word]
    cur.execute(command, criteria)
    row = cur.fetchone()
    
    Word = namedtuple("Word", ["ID", "Word"])
    return Word(row[0], row[1]) if row else None

def MatchDisabledArchetypes(discord_id, user_id):
  days = 30
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.event_date, asu.player_name, asu.archetype_played, asu.date_submitted, asu.submitter_username
    FROM archetypesubmissions asu
    INNER JOIN events e ON e.id = asu.event_id
    WHERE e.discord_id = {discord_id}
      AND asu.submitter_id = {user_id}
      AND asu.reported = {True}
      AND e.event_date BETWEEN current_date - {days} AND current_date
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def DisableMatchingWords(discord_id, word):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    word_inject = "%" + word + "%"
    criteria = [word_inject]
    command = f'''
    UPDATE ArchetypeSubmissions
    SET reported = True
    WHERE event_id IN (
      SELECT id
      FROM events
      WHERE discord_id = {discord_id}
    )
    AND archetype_played LIKE %s
    RETURNING *
    '''
    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return row

def AddBadWordBridge(discord_id, word_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO badwords_stores (discord_id, badword_id)
    VALUES ({discord_id}, {word_id})
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

def CheckStoreBannedWords(discord_id, archetype):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT
      *
    FROM
      badwords b
      INNER JOIN badwords_stores bs ON b.id = bs.badword_id
    WHERE
      bs.discord_id = %s
      AND POSITION(badword IN %s) > 0
    '''

    criteria = [discord_id, archetype]
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def GetOffenders(game, format, store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT 
      CAST(asu.date_submitted AS DATE) as date_submitted,
      asu.submitter_username,
      asu.submitter_id,
      e.event_date,
      {'g.name,' if not game else ''}
      {'f.name,' if not format else ''}
      asu.player_name,
      asu.archetype_played
    FROM ArchetypeSubmissions asu
      INNER JOIN Events e on e.id = asu.event_id
      INNER JOIN Games c on c.id = e.game_id
      INNER JOIN Formats f on f.id = e.format_id
    WHERE asu.reported = {True}
      AND e.discord_id = {store.DiscordId}
      {f'AND e.game_id = {game.GameId}' if game else ''}
      {f'AND e.format_id = {format.FormatId}' if format else ''}
    ORDER BY asu.date_submitted DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows