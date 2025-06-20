import os
import psycopg2
from psycopg2.errors import UniqueViolation

#With this file reaching about 1000 lines, I think it's time to break it up into multiple files with relevant methods in each
conn = psycopg2.connect(os.environ['DATABASE_URL'])

def GetOffenders(game, format, store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT asu.date_submitted,
           asu.submitter_username,
           asu.submitter_id,
           e.event_date,
           {'g.name,' if not game else ''}
           {'f.name,' if not format else ''}
           asu.player_name,
           asu.archetype_played
    FROM ArchetypeSubmissions asu
    INNER JOIN Events e on e.id = asu.event_id
    INNER JOIN CardGames c on c.id = e.game_id
    INNER JOIN Formats f on f.id = e.format_id
    WHERE asu.reported = {True}
    AND e.discord_id = {store.DiscordId}
    {f'AND e.game_id = {game.ID}' if game else ''}
    {f'AND e.format_id = {format.ID}' if format else ''}
    ORDER BY asu.date_submitted DESC
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

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
      return row
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
    rows = cur.fetchall()
    return rows

def GetWordsForDiscord(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT b.badword
    FROM BadWords b
    INNER JOIN badwords_stores bs ON b.id = bs.badword_id
    WHERE bs.discord_id = {discord_id}
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

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

#Currently hardcoded to 30 day time frame, but could be flexible
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

def AddArchetype(event_id,
                 player_name,
                 archetype_played,
                 submitter_id,
                 submitter_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO ArchetypeSubmissions (event_id, player_name, archetype_played, date_submitted, submitter_id, submitter_username, reported)
    VALUES ({event_id}, '{player_name}', '{archetype_played}', NOW(), {submitter_id}, '{submitter_name}', {False})
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row
  
def GetUnknown(discord_id, game_id, format_id, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = f'''
  SELECT
    e.event_date,
    p.player_name
  FROM
    (
      SELECT
        event_id,
        p.player_name
      FROM
        participants p
      UNION
      SELECT
        event_id,
        player1_name AS player_name
      FROM
        rounddetails
      UNION
      SELECT
        event_id,
        player2_name AS player_name
      FROM
        rounddetails
      WHERE player2_name != 'BYE'
    ) p
    INNER JOIN events e ON p.event_id = e.id
    LEFT JOIN (
      SELECT DISTINCT ON (event_id, player_name)
        event_id,
        player_name,
        archetype_played,
        submitter_id
      FROM
        ArchetypeSubmissions
      WHERE
        reported = FALSE
      ORDER BY
        event_id,
        player_name,
        id DESC
    ) ap ON p.event_id = ap.event_id
    AND p.player_name = ap.player_name
  WHERE
    archetype_played IS NULL
    AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    AND e.game_id = {game_id}
    AND e.format_id = {format_id}
    AND e.discord_id = {discord_id}
  ORDER BY e.event_date desc, player_name
  '''

  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetStats(discord_id,
             game,
             format,
             user_id,
             start_date,
             end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = f'''
  WITH X AS (
    SELECT
      {'f.name as format_name,' if not format else ''}
      archetype_played,
      sum(wins) AS wins,
      sum(losses) AS losses,
      sum(draws) AS draws
    FROM
      (
        SELECT
          event_id,
          player_name,
          wins,
          losses,
          draws
        FROM
          participants
        UNION
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
      ) r
      INNER JOIN events e ON r.event_id = e.id
      INNER JOIN formats f ON f.id = e.format_id
      LEFT JOIN (
        SELECT DISTINCT
          ON (event_id, player_name) event_id,
          player_name,
          archetype_played,
          submitter_id
        FROM
          ArchetypeSubmissions
        WHERE
          reported = FALSE
        ORDER BY
          event_id,
          player_name,
          id DESC
      ) asu ON asu.event_id = r.event_id
      AND asu.player_name = r.player_name
    WHERE
      r.player_name = (
        SELECT
          player_name
        FROM
          archetypesubmissions
        WHERE
          submitter_id = {user_id}
        GROUP BY
          player_name
        ORDER BY
          COUNT(*) DESC
        LIMIT
          1
      )
      AND e.discord_id = {discord_id}
      AND e.game_id = {game.ID}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY
      {'f.name,' if not format else ''} 
      archetype_played
  )
  SELECT
    {'format_name,' if not format else ''}
    archetype_played,
    wins,
    losses,
    draws,
    ROUND(100.0 * wins / (wins + losses + draws), 2) AS win_percentage
  FROM
    (
      (
        SELECT
          1 AS rank,
          {"' ' as format_name," if not format else ''}
          'Overall' AS archetype_played,
          sum(wins) AS wins,
          sum(losses) AS losses,
          sum(draws) AS draws
        FROM
          X
      )
      UNION
      (
        SELECT
          2 AS rank,
          {'format_name,' if not format else ''}
          archetype_played,
          wins,
          losses,
          draws
        FROM
          X
      )
    )
  ORDER BY
    rank,
    {'format_name, ' if not format else ''}
    archetype_played
  '''
  
  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    return rows

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

def CreateEvent(event_date,
                discord_id,
                game,
                format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events (event_date, discord_id, game_id, last_update {', format_id' if game.HasFormats else ''})
    VALUES ('{event_date}', {discord_id}, {game.ID}, 0{f' , {format.ID}' if game.HasFormats else ''})
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    event = cur.fetchone()
    return event if event else None


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

def GetEventMeta(event_id):
  criteria = [event_id]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      archetype_played,
      wins
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
    ORDER BY wins desc
    '''
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

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

def GetParticipantId(event_id, player_name):
  criteria = [player_name]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT id
    FROM participants
    WHERE event_id = {event_id}
    AND player_name = %s
    LIMIT 1
    '''
    cur.execute(command, criteria)
    rowid = cur.fetchone()
    return rowid[0] if rowid else None

def Increase(playerid, wins, losses, draws):
  criteria = [wins, losses, draws, playerid]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE participants
    SET wins = wins + {wins},
        losses = losses + {losses},
        draws = draws + {draws}
    WHERE id = {playerid}
    RETURNING *
    '''

    cur.execute(command, criteria)
    conn.commit()
    row = cur.fetchone()
    return row[0] if row else None

def AddResult(event_id,
              player,
              submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      #I'm choosing to inject these values due to player_name technically being a string of user input
      command = '''
      INSERT INTO Participants (event_id, player_name, wins, losses, draws, submitter_id)
      VALUES (%s, %s, %s, %s, %s, %s)
      RETURNING *
      '''
      cur.execute(command, (event_id,
                            player.PlayerName.upper(),
                            player.Wins,
                            player.Losses,
                            player.Draws,
                            submitter_id))

      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None

def GetRoundNumber(event_id):
  criteria = [event_id]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT MAX(round_number)
    FROM rounddetails
    WHERE event_id = {event_id}
    '''

    cur.execute(command, criteria)
    row = cur.fetchone()
    if row is None:
      return 0
    elif row[0] is None:
      return 0
    else:
      return row[0]

def GetBadWord(word):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT id, word
    FROM badwords
    WHERE badword = '{word}'
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row

def AddRoundResult(event_id,
                   round_number,
                   player1id,
                   player2id,
                   winner_id,
                   submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      command = f'''
      INSERT INTO RoundDetails (event_id,
      round_number,
      player1_id,
      {'player2_id,' if player2id else ''}
      {'winner_id,' if winner_id else ''}
      submitter_id)
      VALUES ({event_id},
      {round_number},
      {player1id},
      {f'{player2id}, ' if player2id else ''}
      {f'{winner_id},' if winner_id else ''}
      {submitter_id})
      RETURNING *
      '''
      cur.execute(command)

      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None

def GetFormatByMap(channel_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT f.id, f.name, f.last_ban_update
    FROM formatchannelmaps fc
    INNER JOIN formats f ON f.id = fc.format_id
    WHERE channel_id = {channel_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row

def GetFormatsByGameId(game_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT id, name
    FROM formats
    WHERE game_id = {game_id}
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetEventObj(discord_id,
                date,
                game,
                format,
                player_name = ''):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.id, e.discord_id, e.event_date, e.game_id, e.format_id, e.last_update
    FROM events e
    LEFT JOIN participants p ON e.id = p.event_id
    LEFT JOIN rounddetails rd ON e.id = rd.event_id
    WHERE e.discord_id = {discord_id}
    AND e.game_id = {game.ID}
    {f'AND e.format_id = {format.ID}' if format else ''}
    {f"AND e.event_date = '{date}'" if date else "AND e.event_date BETWEEN current_date - 14 AND current_date"}
    {f"AND (p.player_name = '{player_name}' OR rd.player1_name = '{player_name}' OR rd.player2_name = '{player_name}')" if player_name != '' else ''}
    ORDER BY event_date DESC
    LIMIT 1
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row if row else None

def GetStoreByDiscord(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  f'''
  SELECT discord_id, discord_name, store_name, owner_id, owner_name, isApproved, used_for_data, payment_level
  FROM Stores
  WHERE discord_id = {discord_id}
  '''

  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    return rows if rows else None

#This command is never called, I don't feel it's necessary to delete the store for a demo
def DeleteDemo():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'DELETE FROM Events WHERE discord_id = 1357401531435192431 and id > 12; '
    #command += 'DELETE FROM Stores WHERE discord_id = 1357401531435192431; '
    cur.execute(command)
    conn.commit()
  
def UpdateDemo(event_id, event_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE events
    SET event_date = '{event_date}'
    WHERE id = {event_id}
    '''
    cur.execute(command)
    conn.commit()
  
def GetGameByMap(category_id:int):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT id, name, hasformats
    FROM cardgames g
    INNER JOIN gamecategorymaps gc ON g.id = gc.game_id
    WHERE category_id = {category_id}
    '''
    cur.execute(command)
    row = cur.fetchone()
    return row
    
def GetDataRowsForMetagame(game,
                           format,
                           start_date,
                           end_date,
                           store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      archetype_played,
      ROUND(metagame_percent * 100, 2) AS metagame_percent,
      ROUND(win_percent * 100, 2) AS win_percent,
      ROUND(metagame_percent * win_percent * 100, 2) AS Combined
    FROM
      (
        SELECT
          archetype_played,
          1.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percent,
          COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
        FROM
          (
            SELECT
              COALESCE(X.archetype_played, 'UNKNOWN') AS archetype_played,
              wins,
              losses,
              draws
            FROM
              participants p
              LEFT OUTER JOIN (
                SELECT DISTINCT ON (event_id, player_name)
                  event_id,
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
              ) X ON X.event_id = p.event_id
              AND X.player_name = p.player_name
              INNER JOIN events e ON p.event_id = e.id
              INNER JOIN stores s ON s.discord_id = e.discord_id
            WHERE
              e.event_date BETWEEN '{start_date}' AND '{end_date}'
              {f'AND e.discord_id = {store.DiscordId}' if store else 'AND s.used_for_data = TRUE'}
              AND e.format_id = {format.ID}
              AND e.game_id = {game.ID}
            UNION ALL
            SELECT
              archetype_played,
              COUNT(
                CASE
                  WHEN game_wins > game_losses THEN 1
                END
              ) AS wins,
              COUNT(
                CASE
                  WHEN game_wins < game_losses THEN 1
                END
              ) AS losses,
              COUNT(
                CASE
                  WHEN game_wins = game_losses THEN 1
                END
              ) AS draws
            FROM
              (
                WITH
                  X AS (
                    WITH
                      A AS (
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
                      )
                    SELECT
                      A1.player_name AS player1_name,
                      COALESCE(A1.archetype_played, 'UNKNOWN') AS player1_archetype,
                      player1_game_wins,
                      A2.player_name AS player2_name,
                      COALESCE(A2.archetype_played, 'UNKNOWN') AS player2_archetype,
                      player2_game_wins
                    FROM
                      rounddetails rd
                      INNER JOIN events e ON rd.event_id = e.id
                      INNER JOIN stores s ON e.discord_id = s.discord_id
                      LEFT JOIN A A1 ON A1.event_id = rd.event_id
                      AND A1.player_name = rd.player1_name
                      LEFT JOIN A A2 ON A2.event_id = rd.event_id
                      AND A2.player_name = rd.player2_name
                    WHERE
                      e.event_date BETWEEN '{start_date}' AND '{end_date}'
                      {f'AND e.discord_id = {store.DiscordId}' if store else 'AND s.used_for_data = TRUE'}
                      AND e.format_id = {format.ID}
                      AND e.game_id = {game.ID}
                    ORDER BY
                      rd.event_id DESC,
                      rd.round_number
                  ) (
                    SELECT
                      player1_archetype AS archetype_played,
                      player1_game_wins AS game_wins,
                      player2_game_wins AS game_losses
                    FROM
                      X
                    UNION ALL
                    SELECT
                      player2_archetype AS archetype_played,
                      player2_game_wins AS game_wins,
                      player1_game_wins AS game_losses
                    FROM
                      X
                  )
              )
            GROUP BY
              archetype_played
            ORDER BY
              1
          )
        GROUP BY
          archetype_played
      )
    WHERE
      metagame_percent >= 0.02
    ORDER BY
      4 DESC
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

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
    INSERT INTO RoundDetails (event_id,
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

def GetTopPlayerData(discord_id,
                     game_id,
                     format_id,
                     start_date,
                     end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT player_name,
           round(eventpercent * 100, 2) as eventpercent,
           round(winpercent * 100, 2) as winpercent,
           round(eventpercent * winpercent * 100, 2) as Combined
    FROM (
      SELECT p.player_name,
             COUNT(*) * 1.0 / (
                SELECT COUNT(*)
                FROM events
                WHERE game_id = {game_id}
                AND format_id = {format_id}
                AND discord_id = {discord_id}
                AND event_date BETWEEN '{start_date}' AND '{end_date}'
             ) as eventpercent,
             sum(p.wins) * 1.0 / (sum(p.wins) + sum(p.losses) + sum(p.draws)) as winpercent
      FROM participants p
      INNER JOIN events e ON e.id = p.event_id
      WHERE e.event_date BETWEEN '{start_date}' AND '{end_date}'
        AND game_id = {game_id}
        AND format_id = {format_id}
        AND discord_id = {discord_id}
      GROUP BY p.player_name
    )
    ORDER BY combined desc
    LIMIT 10
    '''
  
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetAllGames():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT id, name, hasFormats
    FROM CardGames
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetPercentage(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      COUNT(
        CASE
          WHEN archetype_played IS NOT NULL THEN 1
        END
      ) / SUM(count(*)) OVER () AS percentage
    FROM
      (
        SELECT
          event_id,
          player_name
        FROM
          participants p
        UNION
        SELECT
          event_id,
          player1_name AS player_name
        FROM
          rounddetails rd
        UNION
        SELECT
          event_id,
          player2_name AS player_name
        FROM
          rounddetails rd
        WHERE
          player2_name != 'BYE'
      ) p
      LEFT OUTER JOIN (
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
      ) X ON X.event_id = p.event_id
      AND X.player_name = p.player_name
    WHERE
      p.event_id = {event_id}    
    """
    cur.execute(command)
    row = cur.fetchone()
    return row[0] if row else None

def UpdateEvent(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    UPDATE events
    SET last_update = last_update + 1
    WHERE id = {event_id}
    RETURNING *
    """
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

def GetAttendance(store,
                 game,
                 format,
                 start_date,
                 end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT e.event_date,
      {'s.store_name,' if not store else ''}
      {'f.name,' if not format else ''}
      COUNT(*)
    FROM Events e
    INNER JOIN Participants p on e.id = p.event_id
    INNER JOIN Stores s on s.discord_id = e.discord_id
    INNER JOIN Formats f on f.id = e.format_id
    WHERE e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game.ID} 
      AND s.used_for_data = {True}
      {f'AND e.discord_id = {store.DiscordId}' if store else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
    GROUP BY e.id
      {', f.name' if not format else ''}
      {', s.store_name' if not store else ''}
    ORDER BY e.event_date DESC
    '''
    print('Command:', command)
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def AddGameMap(discord_id:int,
               game_id:int,
               category_id:int):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO GameCategoryMaps (discord_id, game_id, category_id)
    VALUES ({discord_id}, {game_id}, {category_id})
    ON CONFLICT (discord_id, category_id) DO UPDATE
    SET game_id = {game_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

def AddFormatMap(discord_id:int,
                 format_id:int,
                 channel_id:int):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO FormatChannelMaps (discord_id, format_id, channel_id)
    VALUES ({discord_id}, {format_id}, {channel_id})
    ON CONFLICT (discord_id, channel_id) DO UPDATE
    SET format_id = {format_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row
    