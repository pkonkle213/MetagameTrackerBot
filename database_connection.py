import os
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])

def AddArchetype(event_id,
                 player_name,
                 archetype_played,
                 date_submitted,
                 submitter_id,
                submitter_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO ArchetypeSubmissions (event_id, player_name, archetype_played, date_submitted, submitter_id, submitter_username, reported)
    VALUES ({event_id}, '{player_name}', '{archetype_played}', '{date_submitted}', {submitter_id}, '{submitter_name}', {False})
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row
  
def GetUnknown(discord_id, game_id, format_id, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = f'''
  SELECT e.event_date,
         p.player_name,
         ap.archetype_played
  FROM participants p
  INNER JOIN events e ON e.id = p.event_id
  LEFT OUTER JOIN ArchetypeSubmissions ap ON (ap.event_id = p.event_id AND ap.player_name = p.player_name)
  WHERE e.discord_id = {discord_id}
    AND e.format_id = {format_id}
    AND e.game_id = {game_id}
    AND ap.archetype_played IS NULL
    AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
  ORDER BY e.event_date DESC, p.player_name
  '''

  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    cur.close() #IS THIS WHAT I'VE BEEN MISSING FROM OTHER METHODS!?
    return rows

def GetStats(discord_id,
             game_id,
             format_id,
             user_id,
             start_date,
             end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  
  command = f'''
    SELECT archetype_played,
           wins,
           losses,
           draws,
           ROUND(winpercentage * 100, 2) as winpercentage
    FROM (
    (WITH X AS (
    SELECT DISTINCT on (event_id, player_name)
      event_id, player_name, archetype_played
    FROM ArchetypeSubmissions
    WHERE event_id IN (
      SELECT id
      FROM events e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      WHERE e.discord_id = {discord_id}
      AND e.game_id = {game_id}
      AND e.format_id = {format_id}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      ORDER BY e.event_date DESC
    )
    AND player_name IN (
      SELECT player_name
      FROM ArchetypeSubmissions asu
      INNER JOIN events e ON e.id = asu.event_id
      WHERE submitter_id = {user_id}
      AND discord_id = {discord_id}
      GROUP BY player_name
      ORDER BY COUNT(*) DESC
      LIMIT 1
    )
    ORDER BY event_id, player_name, id desc
    )
    SELECT 1 as Rank, 'OVERALL' as archetype_played, sum(wins) as wins, sum(losses) as losses, sum(draws) as draws, sum(wins) * 1.0 / (sum(wins) + sum(losses)+sum(draws)) as winpercentage
    FROM X
    INNER JOIN participants p ON p.event_id = X.event_id AND p.player_name = X.player_name)
    UNION
    (WITH X AS (
    SELECT DISTINCT on (event_id, player_name)
    event_id, player_name, archetype_played
    FROM ArchetypeSubmissions
    WHERE event_id IN (
    SELECT id
    FROM events e
    INNER JOIN stores s ON s.discord_id = e.discord_id
    WHERE e.discord_id = {discord_id}
    AND e.game_id = {game_id}
    AND e.format_id = {format_id}
    AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY e.event_date DESC
    )
    AND player_name IN (SELECT player_name
    FROM ArchetypeSubmissions asu
    INNER JOIN events e ON e.id = asu.event_id
    WHERE submitter_id = {user_id}
    AND discord_id = {discord_id}
    GROUP BY player_name
    ORDER BY COUNT(*) DESC
    LIMIT 1)
    ORDER BY event_id, player_name, id desc
    )
    SELECT 2 as Rank, COALESCE(X.archetype_played,'UNKNOWN') as archetype_played, sum(wins) as wins, sum(losses) as losses, sum(draws) as draws, sum(wins) * 1.0 / (sum(wins) + sum(losses)+sum(draws)) as winpercentage
    FROM X
    INNER JOIN participants p ON p.event_id = X.event_id AND p.player_name = X.player_name
    GROUP BY archetype_played
    ORDER BY archetype_played)
    )
    ORDER BY rank
  '''
  
  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    cur.close()
    return rows

def GetAnalysis(discord_id, game_id, format_id, weeks, isMeta, dates):
  (EREnd, ERStart, BREnd, BRStart) = dates
  #TODO: Is this proper to do? Saves coding, looks sloppy
  #One formula is for win percentage, the other is for metagame percentage
  formula = 'COUNT(*) * 1.0 / SUM(COUNT(*)) OVER()' if isMeta else '(sum(p.wins) * 1.0) / (sum(p.wins) + sum(p.losses))'
  with conn, conn.cursor() as cur:
    command = f"""
      SELECT archetype_played,
        ROUND(BeginningRange * 100, 2) AS BeginningRange,
        ROUND(EndingRange * 100, 2) AS EndingRange,
        ROUND((EndingRange - BeginningRange) * 100, 2) AS Shift
      FROM (
        SELECT Decks.archetype_played,
          SUM(COALESCE(BeginningRange.StatBR, 0)) AS BeginningRange,
          SUM(COALESCE(EndingRange.StatER, 0)) AS EndingRange
        FROM (
          SELECT DISTINCT archetype_played
          FROM participants
          WHERE event_id IN (
            SELECT id
            FROM events
            WHERE game_id = {game_id}
            AND format_id = {format_id}
            AND discord_id = {discord_id}
            AND event_date >= '{BRStart}'
            AND event_date <= '{EREnd}'
          )
        ) AS Decks
        LEFT OUTER JOIN (
          SELECT p.archetype_played,
            {formula} AS StatBR
          FROM participants p
          INNER JOIN events e ON p.event_id = e.id
          WHERE e.event_date >= '{BRStart}'
          AND e.event_date <= '{BREnd}'
          AND e.game_id = {game_id}
          AND e.format_id = {format_id}
          AND e.discord_id = {discord_id}
          GROUP BY p.archetype_played
        ) AS BeginningRange ON Decks.archetype_played = BeginningRange.archetype_played
        LEFT OUTER JOIN (
          SELECT p.archetype_played,
            {formula} AS StatER
          FROM participants p
          INNER JOIN events e ON p.event_id = e.id
          WHERE e.event_date >= '{ERStart}'
          AND e.event_date <= '{EREnd}'
          AND e.game_id = {game_id}
          AND e.format_id = {format_id}
          AND e.discord_id = {discord_id}
          GROUP BY p.archetype_played
        ) AS EndingRange ON Decks.archetype_played = EndingRange.archetype_played
        GROUP BY Decks.archetype_played
      )
      WHERE EndingRange >=.02 OR BeginningRange >= .02
      ORDER BY Shift DESC, archetype_played
      """
    cur.execute(command)
    rows = cur.fetchall()
    cur.close()
    return rows

def GetStoreData(discord_id, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT c.name AS GameName,
           f.name AS FormatName,
           e.event_date AS EventDate,
           p.player_name AS PlayerName,
           COALESCE(ap.archetype_played,'UNKNOWN') AS ArchetypePlayed,
           p.wins AS Wins,
           p.losses AS Losses,
           p.draws AS Draws
    FROM participants p
      INNER JOIN events e on e.id = p.event_id
      INNER JOIN cardgames c on c.id = e.game_id
      INNER JOIN formats f on f.id = e.format_id
      INNER JOIN stores s on s.discord_id = e.discord_id
      LEFT JOIN ArchetypeSubmissions ap ON (ap.player_name = p.player_name AND ap.event_id = p.event_id)
    WHERE e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.discord_id = {discord_id}
      {f'AND e.format_id = {format.ID}' if format else ''}
    ORDER BY 3 desc, 6 desc
    '''
  
    cur.execute(command)
    rows = cur.fetchall()
    return rows
  
def ViewEvent(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT archetype_played, wins, losses, draws
    FROM participants p
    WHERE event_id = {event_id}
    ORDER BY wins DESC, draws DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def CreateEvent(event_date,
                discord_id,
                game,
                format):
  criteria = [event_date, discord_id, game.ID, 0]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO Events (event_date, discord_id, game_id, last_update {', format_id' if game.HasFormats else ''})
    VALUES ('{event_date}', {discord_id}, {game.ID}, 0{f' , {format.ID}' if game.HasFormats else ''})
    RETURNING *
    '''
    cur.execute(command, criteria)
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
    WITH X AS (
      SELECT DISTINCT on (event_id, player_name)
          event_id, player_name, archetype_played
      FROM ArchetypeSubmissions
      WHERE event_id = {event_id}
      AND reported = {False}
      ORDER BY event_id, player_name, id desc
    )
    SELECT X.archetype_played,
           p.wins
    FROM participants p
    LEFT OUTER JOIN X on X.event_id = p.event_id and X.player_name = p.player_name
    WHERE p.event_id = {event_id}
    ORDER BY p.wins DESC
    '''
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def SetStoreTrackingStatus(approval_status,
                           store_discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'UPDATE Stores SET isApproved = %s '
    command += 'WHERE discord_id = %s returning * '
    criteria = (approval_status, store_discord_id)
    cur.execute(command, criteria)
    conn.commit()
    store = cur.fetchone()
    return store

def GetParticipantId(event_id, player_name):
  criteria = [event_id, player_name]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT id '
    command += 'FROM participants '
    command += 'WHERE event_id = %s '
    command += 'AND player_name = %s '
    command += 'LIMIT 1'
    cur.execute(command, criteria)
    rowid = cur.fetchone()
    return rowid[0] if rowid else None

def Increase(playerid, wins, losses, draws):
  criteria = [wins, losses, draws, playerid]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'UPDATE participants '
    command += 'SET wins = wins + %s, '
    command += 'losses = losses + %s, '
    command += 'draws = draws + %s '
    command += 'WHERE id = %s '

    cur.execute(command, criteria)
    conn.commit()

def AddResult(event_id,
              player,
              submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
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
    command =  'SELECT MAX(round_number) '
    command += 'FROM rounddetails '
    command += 'WHERE event_id = %s '
    command += 'GROUP BY event_id '

    cur.execute(command, criteria)
    row = cur.fetchone()
    return row[0] if row else None

def AddRoundResult(event_id,
                   round_number,
                   player1id,
                   player2id,
                   winner_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      command = 'INSERT INTO rounddetails (event_id, round_number, player1_id, player2_id, winner_id) '
      command += 'VALUES (%s, %s, %s, %s, %s) '
      command += 'RETURNING *     '
      cur.execute(command, (event_id,
                            round_number,
                            player1id,
                            player2id,
                            winner_id))

      conn.commit()
      row = cur.fetchone()
      return row[0] if row else None
    except psycopg2.errors.UniqueViolation:
      return None

def TrackInput(event_id,
               updater_name,
               updater_id,
               archetype_played,
               todays_date,
               player_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = f'''
  INSERT INTO InputTracker (user_name, event_id, user_id, archetype_played, date_submitted, player_name)
  VALUES ('{updater_name}', {event_id}, {updater_id}, '{archetype_played}', '{todays_date}', '{player_name}')
  RETURNING *
  '''
  
  with conn, conn.cursor() as cur:   
    cur.execute(command)
    conn.commit()

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
    SELECT *
    FROM events e
    INNER JOIN participants p ON e.id = p.event_id
    WHERE e.discord_id = {discord_id}
    AND e.game_id = {game.ID}
    {f'AND e.format_id = {format.ID}' if format else ''}
    {f"AND e.event_date = '{date}'" if date else "AND e.event_date BETWEEN current_date - 14 AND current_date"}    
    {f"AND p.player_name = '{player_name}'" if player_name != '' else ''}
    ORDER BY event_date DESC
    LIMIT 1
    '''
    cur.execute(command)
    return cur.fetchone()

def GetStores(name = '',
              discord_id = 0,
              discord_name = '',
              owner = 0,
              approval_status = ''):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  'SELECT discord_id, discord_name, store_name, owner_id, owner_name, isApproved, used_for_data, SpicerackKey '
  command += 'FROM Stores '
  
  criteria = 'WHERE '
  criteria_list = []
  
  if name != '':
    criteria += 'name = %s AND '
    criteria_list.append(name)
  if discord_id != 0:
    criteria += 'discord_id = %s AND '
    criteria_list.append(discord_id)
  if discord_name != '':
    criteria += 'discord_name = %s AND '
    criteria_list.append(discord_name)
  if owner != 0:
    criteria += 'owner = %s AND '
    criteria_list.append(owner)
  if approval_status != '':
    criteria += 'approval_status = %s AND '
    criteria_list.append(approval_status)
  
  if len(criteria_list) == 0:
    raise Exception('No criteria provided')
    
  criteria = criteria[:-4]
  with conn, conn.cursor() as cur:
    cur.execute(command + criteria, criteria_list)
    return cur.fetchall()

def DeleteDemo():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'DELETE FROM Events WHERE discord_id = 1339313300394999931 and id > 12; '
    command += 'DELETE FROM Stores WHERE discord_id = 1339313300394999931; '
    cur.execute(command)
    conn.commit()
  
def UpdateDemo(event_id, event_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'UPDATE events '
    command += 'SET event_date = %s '
    command += 'WHERE id = %s '
    criteria = (event_date, event_id)
    cur.execute(command, criteria)
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
                           discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    criteria = [game.ID, start_date, end_date]
    command = f'''
  SELECT archetype_played,
         ROUND(metagame_percent * 100, 2) AS metagame_percent,
         ROUND(win_percent * 100, 2) AS win_percent,
         ROUND(metagame_percent * win_percent * 100, 2) as Combined
  FROM (
    WITH X AS (
      SELECT DISTINCT on (event_id, player_name)
        event_id, player_name, archetype_played
      FROM ArchetypeSubmissions
      WHERE event_id IN (
        SELECT id
        FROM events e
        INNER JOIN stores s ON s.discord_id = e.discord_id
        WHERE e.discord_id = {discord_id}
        AND e.game_id = {game.ID}
        AND e.format_id = {format.ID}
        AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY e.event_date DESC
      )
      ORDER BY event_id, player_name, id desc
    )
    SELECT COALESCE(X.archetype_played,'UNKNOWN') as archetype_played,
           COUNT(*) * 1.0 / SUM(count(*)) OVER () as Metagame_Percent,
           sum(p.wins) * 1.0 / (sum(p.wins) + sum(p.losses) + sum(p.draws)) as Win_percent
    FROM participants p
    LEFT OUTER JOIN X on X.event_id = p.event_id and X.player_name = p.player_name
    WHERE p.event_id IN (
      SELECT id
      FROM events e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      WHERE e.discord_id = {discord_id}
        AND e.game_id = {game.ID}
        AND e.format_id = {format.ID}
        AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      ORDER BY event_date DESC
    )
    GROUP BY 1
  )
  WHERE metagame_percent >= 0.02
  ORDER BY 4 DESC
    '''
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

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
    command =  'SELECT id, name, hasFormats '
    command += 'FROM CardGames '
    command += 'ORDER BY name '
    cur.execute(command)
    rows = cur.fetchall()
    return rows

#HAHAHAHAH this is awful, but it works
def GetPercentage(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
SELECT (sum / totaldecks) as ReportPercent
FROM (
  SELECT sum(metacount), totaldecks
  FROM (
    SELECT archetype_played, sum(metacount) AS metacount, TotalDecks
    FROM (
      WITH X AS (
        SELECT DISTINCT on (event_id, player_name)
          event_id, player_name, archetype_played
        FROM ArchetypeSubmissions
        WHERE event_id = {event_id}
          AND reported = False
        ORDER BY event_id, player_name, id desc
      )
      SELECT X.archetype_played,
             COUNT(*) AS MetaCount,
             SUM(count(*)) OVER () as TotalDecks
      FROM participants p
      LEFT OUTER JOIN X on X.event_id = p.event_id and X.player_name = p.player_name
      WHERE p.event_id = {event_id}
      GROUP BY 1
    )
    WHERE archetype_played IS NOT NULL
    GROUP BY archetype_played, TotalDecks
  )
  GROUP BY totaldecks
)
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

def GetAttendance(discord_id,
                 game,
                 format,
                 start_date,
                 end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    SELECT e.event_date, COUNT(*)
    FROM events e
    INNER JOIN participants p on e.id = p.event_id
    INNER JOIN Stores s on s.discord_id = e.discord_id
    WHERE e.game_id = {game.ID}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.discord_id = {discord_id}
      AND e.format_id = {format.ID}
    GROUP BY e.id, s.store_name
    ORDER BY e.event_date DESC
    '''
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
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row