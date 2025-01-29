import os
import psycopg2
import date_functions

conn = psycopg2.connect(os.environ['DATABASE_URL'])

def CreateEvent(event_date,
                discord_id,
                game_id,
                format_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'INSERT INTO Events (event_date, discord_id, game_id, format_id) '
    command += 'VALUES (%s, %s, %s, %s) '
    command += 'RETURNING ID'
    criteria = (event_date,
                discord_id,
                game_id,
                format_id)
    
    cur.execute(command, criteria)
    conn.commit()
    event = cur.fetchone()

    return event[0] if event else None


def AddStore(store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'INSERT INTO Stores (store_name, discord_id, discord_name, owner_id, owner_name, isApproved) '
    command += 'VALUES (%s, %s, %s, %s, %s, %s) '
    command += 'returning *'

    cur.execute(command, (store.StoreName,
                          store.DiscordId,
                          store.DiscordName,
                          store.OwnerId,
                          store.OwnerName,
                          False))

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
    
#
def GetFormats(discord_id,
               game):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT event_format '
    command += 'FROM Participants '
    command += 'WHERE discord_id = %s AND game = %s '
    command += 'GROUP BY event_format '
    command += 'ORDER BY event_format'
    criteria = (discord_id, game)

    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

def AddResult(event_id, player, submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      command = 'INSERT INTO Participants (event_id, player_name, archetype_played, wins, losses, draws, submitter_id) '
      command += 'VALUES (%s, %s, %s, %s, %s, %s, %s) '
      cur.execute(command, (event_id,
                            player.PlayerName.upper(),
                            'UNKNOWN',
                            player.Wins,
                            player.Losses,
                            player.Draws,
                            submitter_id))

      conn.commit()
      return 'Success'
    except psycopg2.errors.UniqueViolation:
      return 'Error'


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
    
#
def Claim(event_id,
          name,
          archetype,
          updater_id):
  try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    command =  'UPDATE Participants SET archetype_played = %s, submitter_id = %s '
    command += 'WHERE event_id = %s AND player_name = %s'
    criteria = (archetype, updater_id, event_id, name)
    with conn, conn.cursor() as cur:  
      cur.execute(command, criteria)
      conn.commit()
      #TODO: This doesn't check to see that something was updated
    return 'Success'
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

def GetEventId(discord_id,
               date,
               game_id,
               format_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT id FROM events '
    command += 'WHERE discord_id = %s AND event_date = %s AND game_id = %s AND format_id = %s '
    criteria = (discord_id,
                 date,
                 game_id,
                 format_id)
              
  
    cur.execute(command, criteria)
    rows = cur.fetchall()
    if len(rows) == 0:
      return None
    return rows[0][0]
  

def GetGame(discord_id,
            used_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT cg.id, cg.name FROM cardgames cg '
    command += 'INNER JOIN gamenamemaps gnm ON cg.id = gnm.game_id '
    command += 'WHERE gnm.used_name = %s AND gnm.discord_id = %s '
    criteria = (used_name, discord_id)
    
    cur.execute(command, criteria)
    rows = cur.fetchall()
    if len(rows) == 0:
      return None
    return rows[0]
    
def GetDataRowsForMetagame(game_id,
                           format_id,
                           start_date,
                           end_date,
                           discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    criteria = [game_id, format_id, start_date, end_date]
    command =  'WITH x AS ( '
    command += 'SELECT p.archetype_played, COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () as MetaPercentage, '
    command += '(sum(p.wins) * 1.0) / (sum(p.wins) + sum(p.losses) + sum(p.draws)) as WinPercentage, '
    command += 'FROM Participants p '
    command += 'INNER JOIN Events e ON p.event_id = e.id '
    command += 'WHERE e.game_id = %s '
    #TODO: Maybe I should include unknown archetypes to encourage people to enter info?
    command += 'AND p.archetype_played != \'UNKNOWN\' '
    command += 'AND e.format_id = %s '
    command += 'AND e.event_date >= %s AND event_date <= %s '
    if discord_id != 0:
      command += 'AND e.discord_id = %s '
      criteria.append(discord_id)
    command += 'GROUP BY p.archetype_played '
    command += 'ORDER BY p.archetype_played '
    command += ') '
    command += 'SELECT archetype_played, '
    command += 'CONCAT(TO_CHAR(ROUND(MetaPercentage * 100, 2), \'999D99\'), \'%\') AS MetaPercentage'
    command += 'CONCAT(TO_CHAR(ROUND(WinPercentage * 100, 2), \'999D99\'), \'%\') AS WinPercentage, '
    command += 'CONCAT(TO_CHAR(ROUND(MetaPercentage * WinPercentage * 100, 2), \'999D99\'), \'%\') AS Combined'
    command += 'FROM x '
    command += 'WHERE MetaPercentage >= 0.02 '
    command += 'ORDER BY Combined DESC'
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows

#
def GetStoreNamesByGameFormat(game, format):
  end_date = date_functions.GetToday()
  start_date = date_functions.GetStartDate(end_date)
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT d.event_date, s.Name, count(*) as Attendance FROM Participants d INNER JOIN Stores s on s.discord_id = d.discord_id WHERE d.game = %s AND d.event_format = %s and d.event_date >= %s and d.event_date <= %s GROUP BY d.event_date, s.name ORDER BY d.event_date DESC, s.name '
  with conn, conn.cursor() as cur:
    cur.execute(command, (game, format, start_date, end_date))
    rows = cur.fetchall()
    return rows

#
def GetStores(name = '',
              discord_id = 0,
              discord_name = '',
              owner = 0,
              approval_status = ''):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  'SELECT discord_id, discord_name, store_name, owner_id, owner_name, isApproved '
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
    
#
def GetTopPlayers(discord_id,
                  game_id,
                  format_id,
                  start_date,
                  end_date,
                  top_number):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  criteria = [discord_id, game_id, start_date, end_date]

  with conn, conn.cursor() as cur:
    command = 'SELECT p.player_name, count(*) * 1.0 / sum(count(*)) Over () as MetaPercentage, (sum(p.wins)) / (sum(p.wins) * 1.0 + sum(p.losses) + sum(p.draws)) as WinPercentage, (sum(p.wins)) / (sum(p.wins) * 1.0 + sum(p.losses) + sum(p.draws)) * count(*) / sum(count(*)) Over () as Combined '
    command += 'FROM Participants p '
    command += 'INNER JOIN Events e ON p.event_id = e.id '
    command += 'WHERE e.discord_id = %s '
    command += 'AND e.game_id = %s '
    command += 'AND e.event_date >= %s '
    command += 'AND e.event_date <= %s '

    if format != '':
      criteria.append(format_id)
      command += 'AND e.format_id = %s '

    command += 'GROUP BY p.player_name '
    command += 'ORDER BY Combined DESC '
    command += 'LIMIT %s '
    criteria.append(top_number)

    cur.execute(command, criteria)
    rows = cur.fetchall()  

    return rows

def GetAllGames():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  'SELECT id, name '
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
    
#
def GetPlayersInEvent(discord_id,
                      game,
                      event_date,
                      event_format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  'SELECT player_name, archetype_played, wins, losses, draws '
  command += 'FROM Participants '
  command += 'WHERE game = %s AND discord_id = %s AND event_date = %s AND event_format = %s '
  command += 'ORDER BY player_name ASC'
  with conn, conn.cursor() as cur:
    cur.execute(command, (game, discord_id, event_date, event_format))
    rows = cur.fetchall()
    return rows
    
#
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
    return rows 
    
#
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