import os
import datefuncs
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])

def TrackInput(store_discord, updater_name, updater_id, archetype_played, todays_date, player_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'INSERT INTO InputTracker (user_name, user_id, archetype_played, date_submitted, player_name) VALUES (%s, %s, %s, %s, %s) RETURNING *'
  with conn, conn.cursor() as cur:   
    cur.execute(command, (updater_name,updater_id,archetype_played,todays_date, player_name))
    conn.commit()

def Claim(store_discord, name, archetype, date, format, game, updater):
  try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    command = 'UPDATE DataRows SET archetype_played = %s, submitter = %s WHERE discord_id = %s AND player_name = %s AND event_format = %s AND event_date = %s AND game = %s '
    criteria = (archetype, updater, store_discord, name, format, date, game)
    with conn, conn.cursor() as cur:  
      cur.execute(command, criteria)
      conn.commit()
    return 'Success'
  except Exception as excep:
    return f'Failure: {excep}'

def UpdateDataRow(oldDataRow, newDataRow, submitter_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'UPDATE DataRows SET player_name = %s, archetype_played = %s, wins = %s, losses = %s, draws = %s, submitter = %s '
  command += 'WHERE game = %s AND discord_id = %s AND event_date = %s AND event_format = %s AND player_name = %s '
  criteria = (newDataRow.PlayerName,
              newDataRow.ArchetypePlayed,
              newDataRow.Wins,
              newDataRow.Losses,
              newDataRow.Draws,
              newDataRow.SubmitterId,
              oldDataRow.GamePlayed,
              oldDataRow.LocationDiscordId,
              oldDataRow.DateOfEvent,
              oldDataRow.Format,
              oldDataRow.PlayerName)

  with conn, conn.cursor() as cur:
    try:
      cur.execute(command, criteria)
      conn.commit()
      return 'Successful'
    except psycopg2.errors.UniqueViolation:
      return 'Unable to update row'

def GetStoreOwners():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT owner FROM Stores'
  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def AddStore(store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'INSERT INTO Stores (name, discord_id, discord_name, owner, approval_status) '
    command += 'VALUES (%s, %s, %s, %s, %s) '
    command += 'returning *'

    cur.execute(command, (store.Name,
      store.DiscordId,
      store.DiscordName,
      store.Owner,
      False))

    conn.commit()
    rowid = cur.fetchone()

    return rowid

def ApproveStoreTrackingStatus(store_discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'UPDATE Stores SET approval_status = %s WHERE discord_id = %s returning * '
    cur.execute(command, ('t', store_discord_id))
    conn.commit()
    store = cur.fetchone()
    return store

def RemoveStoreTrackingStatus(store_discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'UPDATE Stores SET approval_status = %s WHERE discord_id = %s returning * '
    cur.execute(command, ('f', store_discord_id))
    conn.commit()
    store = cur.fetchone()
    return store

def DeleteStore(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'DELETE FROM Stores WHERE discord_id = %s'
    cur.execute(command, (discord_id,))
    conn.commit()
    return 'Success'

def GetFormats(discord_id, game):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'SELECT event_format FROM datarows WHERE discord_id = %s AND game = %s GROUP BY event_format ORDER BY event_format'
    cur.execute(command, (discord_id, game))
    rows = cur.fetchall()
    return rows

def AddDataRow(dataRow):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  row = ''
  with conn, conn.cursor() as cur:
    try:
      command = 'INSERT INTO DataRows (game, discord_id, event_date, event_format, player_name, archetype_played, wins, losses, draws, submitter) '
      command += 'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
      command += 'returning *'
      cur.execute(command, (dataRow.GamePlayed.upper(),
                          dataRow.LocationDiscordId,
                          dataRow.DateOfEvent,
                          dataRow.Format.upper(),
                          dataRow.PlayerName.upper(),
                          dataRow.ArchetypePlayed.upper(),
                          dataRow.Wins,
                          dataRow.Losses,
                          dataRow.Draws,
                            dataRow.SubmitterId))
      conn.commit()
      row = cur.fetchone()
    except psycopg2.errors.UniqueViolation:
      print('Error: UniqueViolation')

  return row if row != '' else None

def GetGameName(game):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'SELECT actual_name FROM gamenamemaps WHERE used_name = %s'
    cur.execute(command, (game,))
    rows = cur.fetchall()
    if len(rows) == 0:
      return ''
    return rows[0][0]

def GetDataRowsForMetagame(game,
                           event_format,
                           start_date,
                           end_date,
                           discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    criteria = [game, event_format, start_date, end_date]
    command = 'SELECT archetype_played, COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () as MetaPercentage, (sum(wins)) / (sum(wins) * 1.0 + sum(losses) + sum(draws)) as WinPercentage, (sum(wins)) / (sum(wins) * 1.0 + sum(losses) + sum(draws)) * COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () as Combined '
    command += 'FROM DataRows '
    command += 'WHERE game = %s AND archetype_played != \'UNKNOWN\' AND event_format = %s AND event_date >= %s AND event_date <= %s '
    if discord_id == 0:
      command += 'AND discord_id = %s '
      criteria.append(discord_id)
    command += 'GROUP BY archetype_played '
    command += 'ORDER BY Combined DESC, archetype_played'
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

def AddSubmitter(discord_id,
                 user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      command = 'INSERT INTO Submitters (discord_id, user_id) VALUES (%s, %s) '
      command += 'returning *'
      cur.execute(command, (discord_id, user_id))
      conn.commit()
      row = cur.fetchone()
      return row
    except psycopg2.errors.UniqueViolation:
      print('Error: UniqueViolation')
      return None

def DeleteSubmitter(discord_id,
                    user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'DELETE FROM Submitters WHERE discord_id = %s AND user_id = %s'
    cur.execute(command, (discord_id, user_id))
    conn.commit()
    return 'Success'

def GetSubmitters(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'SELECT user_id FROM Submitters WHERE discord_id = %s'
    cur.execute(command, [discord_id])
    user_ids = cur.fetchall()

    return user_ids

def GetStoreNamesByGameFormat(game, format):
  end_date = datefuncs.GetToday()
  start_date = datefuncs.GetStartDate(end_date)
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT d.event_date, s.Name, count(*) as Attendance FROM datarows d INNER JOIN Stores s on s.discord_id = d.discord_id WHERE d.game = %s AND d.event_format = %s and d.event_date >= %s and d.event_date <= %s GROUP BY d.event_date, s.name ORDER BY d.event_date DESC, s.name '
  with conn, conn.cursor() as cur:
    cur.execute(command, (game, format, start_date, end_date))
    rows = cur.fetchall()
    return rows

def GetStores(name='',
              discord_id=0,
              discord_name='',
              owner=0,
              approval_status=''):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT * FROM Stores '

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

def GetTopPlayers(discord_id,
                  game,
                  format,
                  start_date,
                  end_date,
                  top_number):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  criteria = [discord_id, game, start_date, end_date]

  with conn, conn.cursor() as cur:
    command = f'SELECT TOP {top_number} player_name, count(*) * 1.0 / sum(count(*)) Over () as MetaPercentage, (sum(wins)) / (sum(wins) * 1.0 + sum(losses) + sum(draws)) as WinPercentage, (sum(wins)) / (sum(wins) * 1.0 + sum(losses) + sum(draws)) * count(*) / sum(count(*)) Over () as Combined '
    command += 'FROM DataRows '
    command += 'WHERE discord_id = %s '
    command += 'AND game = %s '
    command += 'AND event_date >= %s '
    command += 'AND event_date <= %s '

    if format != '':
      criteria.append(format)
      command += 'AND event_format = %s '

    command += 'GROUP BY player_name '
    command += 'ORDER BY Combined DESC '

    cur.execute(command, criteria)
    rows = cur.fetchall()  

    return rows

def GetAllGames():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = 'SELECT actual_name FROM gamenamemaps GROUP BY actual_name ORDER BY actual_name '
    cur.execute(command)
    rows = cur.fetchall()
    return rows

#TODO: If no format is provided, it should return all formats
#TODO: If no game is provided, it should consider all games
def GetEvents(discord_id,
              start_date,
              end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT event_date, game, event_format, count(*) FROM DataRows WHERE discord_id = %s AND event_date >= %s AND event_date <= %s GROUP BY (game, event_date, event_format) ORDER BY event_date DESC, event_format '

  with conn, conn.cursor() as cur:
    cur.execute(command, (discord_id, start_date, end_date))
    rows = cur.fetchall()

    return rows

def GetPlayersInEvent(discord_id,
                      game,
                      event_date,
                      event_format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = 'SELECT player_name, archetype_played, wins, losses, draws FROM DataRows WHERE game = %s AND discord_id = %s AND event_date = %s AND event_format = %s ORDER BY player_name ASC'
  with conn, conn.cursor() as cur:
    cur.execute(command, (game, discord_id, event_date, event_format))
    rows = cur.fetchall()
    return rows

# Putting this here in case it's usable later
def GetColumnNames(table):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'SELECT column_name FROM information_schema.columns where table_name = \'{table}\''
    cur.execute(command)
    rows = cur.fetchall()
    return rows   

def AddGameMap(used_name, actual_name):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    try:
      command = 'INSERT INTO GameNameMaps (used_name, actual_name) VALUES (%s, %s) '
      command += 'returning *'
      cur.execute(command, (used_name, actual_name))
      conn.commit()
      row = cur.fetchone()
      return row
    except psycopg2.errors.UniqueViolation:
      return (used_name, actual_name)