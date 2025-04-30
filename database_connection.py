import os
import psycopg2
import settings

conn = psycopg2.connect(os.environ['DATABASE_URL'])

def GetStats(discord_id, game_id, format_id, user_id, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  
  command = f'''
  SELECT archetype_played,
    wins,
    losses,
    draws,
    winpercentage
  FROM
  (
    (
      SELECT 2,
        archetype_played, 
        SUM(wins) AS wins, 
        SUM(losses) as Losses, 
        SUM(draws) as draws,
        ROUND((SUM(wins) * 100.0) / (SUM(wins) + SUM(losses) + SUM(draws)), 2) AS WinPercentage
      FROM participants p
      INNER JOIN events e ON e.id = p.event_id
      WHERE p.player_name = (
        SELECT player_name
        FROM (  
          SELECT DISTINCT ON (e.id, it.user_id, it.player_name) e.id, it.user_id, it.player_name
          FROM inputtracker it
            INNER JOIN events e ON e.id = it.event_id
          WHERE it.user_id = {user_id}
            AND e.discord_id = {discord_id}
            AND e.game_id = {game_id}
            AND e.format_id = {format_id}
          )
        GROUP BY (user_id, player_name)
        ORDER BY COUNT(*) DESC
        LIMIT 1
      )
        AND e.game_id = {game_id}
        AND e.format_id = {format_id}
        AND e.discord_id = {discord_id}
        AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      GROUP BY archetype_played
    )
    UNION
    (
      SELECT 1,
      'Overall', 
      SUM(wins) AS wins, 
      SUM(losses) as Losses, 
      SUM(draws) as draws,
      ROUND((SUM(wins) * 100.0) / (SUM(wins) + SUM(losses) + SUM(draws)), 2) AS WinPercentage
      FROM participants p
      INNER JOIN events e ON e.id = p.event_id
      WHERE p.player_name = (
        SELECT player_name
        FROM (  
          SELECT DISTINCT ON (e.id, it.user_id, it.player_name) e.id, it.user_id, it.player_name
          FROM inputtracker it
            INNER JOIN events e ON e.id = it.event_id
          WHERE it.user_id = {user_id}
            AND e.discord_id = {discord_id}
            AND e.game_id = {game_id}
            AND e.format_id = {format_id}
          )
        GROUP BY (user_id, player_name)
        ORDER BY COUNT(*) DESC
        LIMIT 1
      )
        AND e.game_id = {game_id}
        AND e.format_id = {format_id}
        AND e.discord_id = {discord_id}
        AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      GROUP BY player_name
    )
  )
  '''
  
  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    cur.close()
    if not rows:
      raise Exception('No data found. Please use the /claim command to submit your data.')
    return rows

#Is this proper to do? Saves coding, looks wonky
def GetAnalysis(discord_id, game_id, format_id, weeks, isMeta, dates):
  (EREnd, ERStart, BREnd, BRStart) = dates
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

#TODO: Clean up as a single string
def GetStoreData(discord_id, start_date, end_date):
  criteria = [start_date, end_date]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT c.name AS GameName, '
    command += 'f.name AS FormatName, '
    command += 'e.event_date AS EventDate, '
    command += 'p.player_name AS PlayerName, '
    command += 'p.archetype_played AS ArchetypePlayed, '
    command += 'p.wins AS Wins, '
    command += 'p.losses AS Losses, '
    command += 'p.draws AS Draws '
    command += 'FROM participants p '
    command += 'INNER JOIN events e on e.id = p.event_id '
    command += 'INNER JOIN cardgames c on c.id = e.game_id '
    command += 'INNER JOIN formats f on f.id = e.format_id '
    command += 'INNER JOIN stores s on s.discord_id = e.discord_id '
    command += 'WHERE e.event_date >= %s '
    command += 'AND e.event_date <= %s '
    if discord_id != settings.DATAGUILDID:
      criteria.append(discord_id)
      command += 'AND e.discord_id = %s '
    else:
      command += 'AND s.used_for_data = true '
    command += 'ORDER BY e.event_date, p.wins DESC '

    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows
  
def ViewEvent(event_id):
  criteria = [event_id]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = """
    SELECT archetype_played, wins, losses, draws
    FROM participants p
    WHERE event_id = %s
    ORDER BY wins DESC, draws DESC
    """

    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def CreateEvent(event_date,
                discord_id,
                game,
                format):
  criteria = [event_date, discord_id, game.ID, 0]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'INSERT INTO Events (event_date, discord_id, game_id, last_update'
    if game.HasFormats:
      command += ', format_id'
      criteria.append(format.ID)
    command += ') '
    command += 'VALUES (%s, %s, %s, %s'
    if game.HasFormats:
      command += ', %s'
    command += ') '
    command += 'RETURNING *'

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
    command =  'INSERT INTO Stores (store_name, discord_id, discord_name, owner_id, owner_name, isApproved, used_for_data) '
    command += 'VALUES (%s, %s, %s, %s, %s, %s, %s) '
    command += 'RETURNING *'

    cur.execute(command, (store_name,
                          discord_id,
                          discord_name,
                          owner_id,
                          owner_name,
                          False,
                          True)
               )

    conn.commit()
    rowid = cur.fetchone()

    return rowid

def GetEventMeta(event_id):
  criteria = [event_id]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT archetype_played, wins
    FROM participants
    WHERE event_id = {event_id}
    ORDER BY wins DESC
    """
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
      command = 'INSERT INTO Participants (event_id, player_name, archetype_played, wins, losses, draws, submitter_id) '
      command += 'VALUES (%s, %s, %s, %s, %s, %s, %s) '
      command += 'RETURNING *     '
      cur.execute(command, (event_id,
                            player.PlayerName.upper(),
                            'UNKNOWN',
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

def TrackInput(store_discord,
               event_id,
               updater_name,
               updater_id,
               archetype_played,
               todays_date,
               player_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  'INSERT INTO InputTracker (user_name, event_id, user_id, archetype_played, date_submitted, player_name) '
  command += 'VALUES (%s, %s, %s, %s, %s, %s)'
  criteria = (updater_name,
              event_id,
              updater_id,
              archetype_played,
              todays_date,
              player_name)
  
  with conn, conn.cursor() as cur:   
    cur.execute(command, criteria)
    conn.commit()

def GetSpiceId(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = f'''
  SELECT spicerack_id
  FROM events
  WHERE spicerack_id = {event_id}
  '''
  with conn, conn.cursor() as cur:
    cur.execute(command)
    row = cur.fetchone()
    return row[0] if row else None

def Claim(event_id,
          name,
          archetype,
          updater_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  'UPDATE Participants '
  command += 'SET archetype_played = %s, submitter_id = %s '
  command += 'WHERE event_id = %s '
  command += 'AND player_name = %s '
  command += 'RETURNING *'

  criteria = (archetype, updater_id, event_id, name)
  with conn, conn.cursor() as cur:  
    cur.execute(command, criteria)
    conn.commit()

    row = cur.fetchone()
    return row

def GetFormat(game_id,
              format_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT id, name FROM Formats '
    command += 'WHERE game_id =  %s AND name = %s '
    criteria = (game_id, format_name)
    
    cur.execute(command, criteria)
    rows = cur.fetchall()
    if len(rows) == 0:
      return None
  return rows[0]

def GetEvent(discord_id,
             date,
             game,
             format):
  criteria = [discord_id,
              game.ID]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT id, discord_id, event_date, game_id, format_id, last_update, spicerack_id '
    command += 'FROM events '
    command += 'WHERE discord_id = %s '
    command += 'AND game_id = %s '
    if date is not None:
      command += 'AND event_date = %s '
      criteria.append(date)
    if format != '':
      command += 'AND format_id = %s '
      criteria.append(format.ID)
    command += 'ORDER BY event_date DESC '
    command += 'LIMIT 1'

    cur.execute(command, criteria)
    rows = cur.fetchall()
    if len(rows) == 0:
      return None
    return rows[0]

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
    rows = cur.fetchall()
    return rows

def GetAllFormats(game_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT id, name
    FROM Formats
    WHERE game_id = %s
    '''
    criteria = [game_id]
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

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
  
def GetGame(discord_id,
            used_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  '''
    SELECT cg.id, cg.name, cg.hasFormats
    FROM cardgames cg
    INNER JOIN gamenamemaps gnm ON cg.id = gnm.game_id
    WHERE gnm.used_name = %s
    AND gnm.discord_id = %s
    '''
    criteria = (used_name, discord_id)
    
    cur.execute(command, criteria)
    rows = cur.fetchall()
    if len(rows) == 0:
      return None
    return rows[0]
    
def GetDataRowsForMetagame(game,
                           format,
                           start_date,
                           end_date,
                           discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    criteria = [game.ID, start_date, end_date]
    command = ''
    command += 'WITH x AS ( '
    command += 'SELECT p.archetype_played, COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () as MetaPercentage, '
    command += '(sum(p.wins) * 1.0) / (sum(p.wins) + sum(p.losses)) as WinPercentage '
    command += 'FROM Participants p '
    command += 'INNER JOIN Events e ON p.event_id = e.id '
    command += 'INNER JOIN Stores s on e.discord_id = s.discord_id '
    command += 'WHERE e.game_id = %s '
    command += 'AND e.event_date >= %s AND event_date <= %s '
    if game.HasFormats:
      command += 'AND e.format_id = %s '
      criteria.append(format.ID)
    if discord_id != settings.DATAGUILDID:
      command += 'AND e.discord_id = %s '
      criteria.append(discord_id)
    else:
      command += 'and s.used_for_data = true '
    command += 'GROUP BY p.archetype_played '
    command += 'ORDER BY p.archetype_played '
    command += ') '
    command += 'SELECT archetype_played, '
    command += 'ROUND(MetaPercentage * 100, 2) AS MetaPercentage, '
    command += 'ROUND(WinPercentage * 100, 2) AS WinPercentage, '
    command += 'ROUND(MetaPercentage * WinPercentage * 100, 2) AS Combined '
    command += 'FROM x '
    command += 'WHERE MetaPercentage >= 0.02 '
    command += 'ORDER BY Combined DESC, archetype_played'

    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def GetBanDate(format_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  criteria = [format_id]

  with conn, conn.cursor() as cur:
    command = '''
    SELECT last_ban_update
    FROM formats
    WHERE id = %s
    '''

    cur.execute(command, criteria)
    rows = cur.fetchone()
    print('Ban Update Result:',rows)
    return rows if rows else None

def GetTopPlayers(discord_id,
                  game_id,
                  format,
                  start_date,
                  end_date,
                  top_number):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT player_name,
      round(eventpercent * 100, 2) as eventpercent,
      round(winpercent * 100, 2) as winpercent,
      round(eventpercent * winpercent * 100, 2) as Combined
    FROM (SELECT player_name,
        count(*) * 1.0 /
        (SELECT COUNT(*)
          FROM events
          WHERE game_id = {game_id} 
    '''

    if discord_id != settings.DATAGUILDID:
      command += f'AND discord_id = {discord_id} '
      
    if format != '':
      command += f'AND format_id = {format.ID} '
         
    command += f'''
          AND event_date BETWEEN '{start_date}' AND '{end_date}') AS eventpercent,
        (sum(wins) * 1.0) / (sum(wins) + sum(losses) + sum(draws)) as winpercent
      FROM events e
      INNER JOIN participants p ON p.event_id = e.id
      WHERE game_id = 1
      '''
    
    if discord_id != settings.DATAGUILDID:
      command += f'AND discord_id = {discord_id} '

    if format != '':
      command += f'AND format_id = {format.ID} '
    
    command += f'''
      AND event_date BETWEEN '{start_date}' AND '{end_date}'
      GROUP BY player_name)
    ORDER BY combined desc
    LIMIT {top_number}
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

def GetPercentage(event_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT 1 - metapercent AS ReportedPercent
    FROM (
      SELECT archetype_played, COUNT(*) / SUM(COUNT(*)) OVER () AS MetaPercent
      FROM Participants
      WHERE event_id = {event_id}
      GROUP BY archetype_played
    )
    WHERE archetype_played = 'UNKNOWN'
    """
    cur.execute(command)
    rows = cur.fetchall()
    return rows[0][0] if rows else 1

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

def GetAttendance(discord_id,
                 game,
                 format,
                 start_date,
                 end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  criteria = [game.ID, start_date, end_date]
  with conn, conn.cursor() as cur:
    command =  'SELECT e.event_date, '
    if discord_id == settings.DATAGUILDID:
      command += 's.store_name, '
    command += 'COUNT(*) '
    command += 'FROM events e '
    command += 'INNER JOIN participants p on e.id = p.event_id '
    command += 'INNER JOIN Stores s on s.discord_id = e.discord_id '
    command += 'WHERE e.game_id = %s '
    command += 'AND e.event_date >= %s '
    command += 'AND e.event_date <= %s '
    if discord_id != settings.DATAGUILDID:
      command += 'AND e.discord_id = %s '
      criteria.append(discord_id)
    else:
      command += 'AND s.used_for_data = true '
    if format != '':
      command += 'AND e.format_id = %s '
      criteria.append(format.ID)
    command += 'GROUP BY e.id, s.store_name '
    command += 'ORDER BY e.event_date DESC '
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def GetData(databasename):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'SELECT * FROM {databasename}'
    cur.execute(command, [databasename])
    rows = cur.fetchall()
    return rows

# Putting this here in case it's usable later, it should probably go with GetData
def GetColumnNames(table):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = \'{table}\'
    ORDER BY ordinal_position
    '''
    cur.execute(command)
    rows = cur.fetchall()
    print('Column Names:', rows)
    return rows 
    
def AddGameMap(discord_id, game_id, used_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      command =  'INSERT INTO GameNameMaps (discord_id, game_id, used_name) '
      command += 'VALUES (%s, %s, %s) '
      command += 'RETURNING *'
      criteria = (discord_id, game_id, used_name)
      cur.execute(command, criteria)
      conn.commit()
      row = cur.fetchone()
      return row
    except psycopg2.errors.UniqueViolation:
      return None