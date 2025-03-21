import os
import psycopg2
import settings
import date_functions

conn = psycopg2.connect(os.environ['DATABASE_URL'])

def GetAnalysisDates(weeks):
  EREnd = date_functions.GetToday()
  ERStart = date_functions.GetWeeksAgo(EREnd, weeks)
  BREnd = date_functions.GetDaysAgo(ERStart, 1)
  BRStart = date_functions.GetWeeksAgo(BREnd, weeks)
  return (EREnd, ERStart, BREnd, BRStart)

def GetMetaAnalysis(discord_id, game_id, format_id, weeks):
  (EREnd, ERStart, BREnd, BRStart) = GetAnalysisDates(weeks)
  cur = conn.cursor()
  command = f"""
    SELECT archetype_played,
      ROUND(BeginningRangeMeta * 100, 2) AS BeginningRangeMeta,
      ROUND(EndingRangeMeta * 100, 2) AS EndingRangeMeta,
      ROUND((EndingRangeMeta - BeginningRangeMeta) * 100, 2) AS MetaShift
    FROM (
      SELECT Decks.archetype_played,
        SUM(COALESCE(BeginningRange.MetaPercentBR, 0)) AS BeginningRangeMeta,
        SUM(COALESCE(EndingRange.MetaPercentER, 0)) AS EndingRangeMeta    
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
          COUNT(*) * 1.0 / SUM(COUNT(*)) OVER() AS MetaPercentBR
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
          COUNT(*) * 1.0 / SUM(COUNT(*)) OVER() AS MetaPercentER
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
    ORDER BY MetaShift DESC, archetype_played
    """
  cur.execute(command)
  rows = cur.fetchall()
  cur.close()
  return rows

def GetWinRateAnalysis(discord_id, game_id, format_id, weeks):
  (EREnd, ERStart, BREnd, BRStart) = GetAnalysisDates(weeks)
  cur = conn.cursor()
  command = f"""
    SELECT archetype_played,
      ROUND(BeginningRangeWinRate * 100, 2) AS BeginningRangeWinRate,
      ROUND(EndingRangeWinRate * 100, 2) AS EndingRangeWinRate,
      ROUND((EndingRangeWinRate - BeginningRangeWinRate) * 100, 2) AS WinRateShift
    FROM (
      SELECT Decks.archetype_played,
        SUM(COALESCE(BeginningRange.WinRatePercentBR, 0)) AS BeginningRangeWinRate,
        SUM(COALESCE(EndingRange.WinRatePercentER, 0)) AS EndingRangeWinRate
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
          (sum(p.wins) * 1.0) / (sum(p.wins) + sum(p.losses)) as WinRatePercentBR
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
          (sum(p.wins) * 1.0) / (sum(p.wins) + sum(p.losses)) as WinRatePercentER
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
    ORDER BY MetaShift DESC
    """
  cur.execute(command)
  rows = cur.fetchall()
  cur.close()
  return rows

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
    command += 'ORDER BY e.id, p.wins DESC '

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
  criteria = [event_date, discord_id, game.ID]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'INSERT INTO Events (event_date, discord_id, game_id'
    if game.HasFormats:
      command += ', format_id'
      criteria.append(format.ID)
    command += ') '
    command += 'VALUES (%s, %s, %s'
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
    command += 'returning *'

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
               updater_name,
               updater_id,
               archetype_played,
               todays_date,
               player_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  'INSERT INTO InputTracker (user_name, user_id, archetype_played, date_submitted, player_name, discord_id) '
  command += 'VALUES (%s, %s, %s, %s, %s, %s)'
  criteria = (updater_name,
              updater_id,
              archetype_played,
              todays_date,
              player_name,
              store_discord)
  
  with conn, conn.cursor() as cur:   
    cur.execute(command, criteria)
    conn.commit()
    
def Claim(event_id,
          name,
          archetype,
          updater_id):
  try:
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
  #TODO: This should be more specific and relay why there was a failure to Phil
  except Exception as excep:
    print('My exception:', excep)
    return f'Failure: {excep}'

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
    command =  'SELECT id, discord_id, event_date, game_id, format_id '
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
  command =  'SELECT discord_id, discord_name, store_name, owner_id, owner_name, isApproved, used_for_data '
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
  
  criteria = criteria[:-4] if len(criteria) != 6 else ''
  with conn, conn.cursor() as cur:
    cur.execute(command + criteria, criteria_list)
    rows = cur.fetchall()
    return rows

def GetAllFormats(game_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT id, name FROM Formats '
    command += 'WHERE game_id = %s '
    criteria = (game_id,)
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def DeleteDemo():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'DELETE FROM Events WHERE discord_id = 1339313300394999931 and id > 40; '
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
    command =  'SELECT cg.id, cg.name, cg.hasFormats FROM cardgames cg '
    command += 'INNER JOIN gamenamemaps gnm ON cg.id = gnm.game_id '
    command += 'WHERE gnm.used_name = %s AND gnm.discord_id = %s '
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
    #TODO: Can I ensure that Unknown is at the bottom of this list?
    command += 'AND p.archetype_played != \'UNKNOWN\' '
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

def GetTopPlayers(discord_id,
                  game_id,
                  format,
                  start_date,
                  end_date,
                  top_number):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  criteria = [game_id, start_date, end_date]

  with conn, conn.cursor() as cur:
    command =  ''
    command += 'WITH x AS ( '
    command += 'SELECT p.player_name, count(*) * 1.0 / sum(count(*)) Over () as MetaPercentage, '
    command += '(sum(p.wins)) / (sum(p.wins) * 1.0 + sum(p.losses) + sum(p.draws)) as WinPercentage '
    command += 'FROM Participants p '
    command += 'INNER JOIN Events e ON p.event_id = e.id '
    command += 'INNER JOIN Stores s on e.discord_id = s.discord_id '
    command += 'WHERE s.used_for_data = True '
    command += 'AND e.game_id = %s '
    command += 'AND e.event_date >= %s '
    command += 'AND e.event_date <= %s '

    if discord_id != settings.DATAGUILDID:
      command += 'AND e.discord_id = %s '
      criteria.append(discord_id)

    if format != '':
      criteria.append(format.ID)
      command += 'AND e.format_id = %s '

    command += 'GROUP BY p.player_name '
    command += ') '
    command += 'SELECT player_name, '
    command += 'ROUND(MetaPercentage * 100, 2) AS MetaPercentage, '
    command += 'ROUND(WinPercentage * 100, 2) AS WinPercentage, '
    command += 'ROUND(MetaPercentage * WinPercentage * 100, 2) AS Combined '
    command += 'FROM x '
    command += 'ORDER BY Combined DESC, player_name '
    command += 'LIMIT %s '
    criteria.append(top_number)

    cur.execute(command, criteria)
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

#TODO: If no format is provided, it should return all formats
#TODO: If no game is provided, it should consider all games
def GetEvents(discord_id,
              start_date,
              end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT event_date, game, event_format, count(*) FROM Participants WHERE discord_id = %s AND event_date >= %s AND event_date <= %s GROUP BY (game, event_date, event_format) ORDER BY event_date DESC, event_format '

  with conn, conn.cursor() as cur:
    cur.execute(command, (discord_id, start_date, end_date))
    rows = cur.fetchall()

    return rows
    
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
    command = f'SELECT column_name FROM information_schema.columns where table_name = \'{table}\''
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