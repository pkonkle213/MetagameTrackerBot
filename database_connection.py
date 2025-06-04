import os
import psycopg2
from settings import DATAGUILDID
from psycopg2.errors import UniqueViolation

#With this file reaching about 1000 lines, I think it's time to break it up into multiple files with relevant methods in each
conn = psycopg2.connect(os.environ['DATABASE_URL'])

def GetStoreReportedPercentage(discord_id,
                              game,
                              format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.event_date,
      {'f.name,' if not format else ''}
      ROUND(100.0 * COUNT(*) FILTER (WHERE archetype_played IS NOT NULL) / COUNT(*), 2) as reported_percent
    FROM (
      SELECT e.id, asu.archetype_played
      FROM Events e
      INNER JOIN participants p on p.event_id = e.id
      LEFT JOIN (SELECT DISTINCT on (event_id, player_name)
                   event_id, player_name, archetype_played, submitter_id
                 FROM ArchetypeSubmissions
                 ORDER BY event_id, player_name, id desc) asu ON asu.event_id = e.id and asu.player_name = p.player_name
      WHERE e.discord_id = {discord_id}
        AND game_id = {game.ID}
        {f'AND format_id = {format.ID}' if format else ''}
      ORDER BY e.id desc
    ) x
    INNER JOIN events e ON x.id = e.id
    INNER JOIN formats f ON f.id = e.format_id
    GROUP BY e.event_date{', f.name' if not format else ''}
    ORDER BY e.event_date desc{', name' if not format else ''}
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def AnalyizeRoundByRound(event_id):
  #Not yet implemented
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
    select rd.round_number,
           X1.archetype_played as player_one_archetype,
           X2.archetype_played as player_two_archetype,
           X3.archetype_played as winner_archetype
    from rounddetails rd
    inner join participants po on rd.player1_id = po.id
    left join X as X1 on X1.event_id = rd.event_id and X1.player_name = po.player_name
    inner join participants pt on rd.player2_id = pt.id
    left join X as X2 on X2.event_id = rd.event_id and X2.player_name = pt.player_name
    inner join participants w on rd.winner_id = w.id
    left join X as X3 on X3.event_id = rd.event_id and X3.player_name = w.player_name
    order by rd.round_number, rd.player1_id
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows

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

#TODO: Probably should inject the word instead of having it in the string. Safety and all that jazz
def DisableMatchingWords(discord_id, word):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    UPDATE ArchetypeSubmissions
    SET reported = True
    WHERE event_id IN (
      SELECT id
      FROM events
      WHERE discord_id = {discord_id}
    )
    AND archetype_played LIKE '%{word}%'
    RETURNING *
    '''
    cur.execute(command)
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
    return rows

#TODO: Check that this doesn't display disabled archetypes
def GetStats(discord_id,
             game,
             format,
             user_id,
             start_date,
             end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command = f'''
  WITH X AS (
    SELECT {'f.name as format_name,' if not format else ''}
      COALESCE(archetype_played,'UNKNOWN') as archetype_played,
      sum(wins) as wins,
      sum(losses) as losses,
      sum(draws) as draws
    FROM participants p
    INNER JOIN events e ON e.id = p.event_id
    INNER JOIN formats f ON f.id = e.format_id
    LEFT JOIN (SELECT DISTINCT on (event_id, player_name)
                 event_id, player_name, archetype_played, submitter_id
               FROM ArchetypeSubmissions
               ORDER BY event_id, player_name, id desc) asu ON asu.event_id = e.id and asu.player_name = p.player_name
    WHERE p.player_name = (SELECT player_name
                           FROM archetypesubmissions
                           WHERE submitter_id = {user_id}
                           GROUP BY player_name
                           ORDER BY count(*) desc
                           LIMIT 1)
      AND discord_id = {discord_id}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.game_id = {game.ID}
    GROUP BY {'f.name,' if not format else ''} archetype_played)
  SELECT  archetype_played,
          {'format_name,' if not format else ''}
          wins,
          losses,
          draws,
          1.0 * wins / (wins + losses + draws) as win_percentage
  FROM  ((SELECT '1' as rank,
            'Overall' as archetype_played,
            {"' ' as format_name," if not format else ''}
            sum(wins) as wins,
            sum(losses) as losses,
            sum(draws) as draws
          FROM X)
          UNION
         (SELECT '2' as rank,
            {'format_name,' if not format else ''}
            archetype_played,
            wins,
            losses,
            draws
          FROM X))
  ORDER BY rank, {'format_name, ' if not format else ''} archetype_played
  '''
  
  with conn, conn.cursor() as cur:
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetStoreData(store, game, format, start_date, end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  f'''
    WITH X AS (
      SELECT DISTINCT on (event_id, player_name)
      event_id, player_name, archetype_played
    FROM ArchetypeSubmissions
    WHERE event_id IN (
      SELECT id
      FROM events e
      INNER JOIN stores s ON s.discord_id = e.discord_id
      WHERE e.discord_id = {store.DiscordId}
      {f'AND e.game_id = {game.ID}' if game else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      ORDER BY e.event_date DESC
      )
    AND reported = {False}
    ORDER BY event_id, player_name, id desc
    )
    SELECT c.name AS GameName,
           f.name AS FormatName,
           e.event_date AS EventDate,
           p.player_name AS PlayerName,
           COALESCE(X.archetype_played,'UNKNOWN') AS ArchetypePlayed,
           p.wins AS Wins,
           p.losses AS Losses,
           p.draws AS Draws
    FROM participants p
      INNER JOIN events e on e.id = p.event_id
      INNER JOIN cardgames c on c.id = e.game_id
      INNER JOIN formats f on f.id = e.format_id
      LEFT JOIN X ON (X.player_name = p.player_name AND X.event_id = p.event_id)
    WHERE e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.discord_id = {store.DiscordId}
      {f'AND e.game_id = {game.ID}' if game else ''}
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
  criteria = [event_id, player_name]
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command =  '''
    SELECT id
    FROM participants
    WHERE event_id = %s
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
    row = cur.fetchone()
    return row if row else None

def GetStoreByDiscord(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  command =  f'''
  SELECT discord_id, discord_name, store_name, owner_id, owner_name, isApproved, used_for_data, SpicerackKey
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
                           store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
      WITH X AS (
        SELECT DISTINCT on (event_id, player_name)
          event_id, player_name, archetype_played
        FROM ArchetypeSubmissions
        WHERE event_id IN (
          SELECT id
          FROM events e
          INNER JOIN stores s ON s.discord_id = e.discord_id
          WHERE e.game_id = {game.ID}
          AND e.format_id = {format.ID}
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
          {f'AND e.discord_id = {store.DiscordId}' if store else ''}
          ORDER BY e.event_date DESC
        )
        AND reported = {False}
        ORDER BY event_id, player_name, id desc
      )
      SELECT COALESCE(X.archetype_played,'UNKNOWN') as archetype_played,
    SELECT archetype_played,
           ROUND(metagame_percent * 100, 2) AS metagame_percent,
           ROUND(win_percent * 100, 2) AS win_percent,
           ROUND(metagame_percent * win_percent * 100, 2) as Combined
    FROM (
             COUNT(*) * 1.0 / SUM(count(*)) OVER () as Metagame_Percent,
             sum(p.wins) * 1.0 / (sum(p.wins) + sum(p.losses) + sum(p.draws)) as Win_percent
      FROM participants p
      LEFT OUTER JOIN X on X.event_id = p.event_id and X.player_name = p.player_name
      WHERE p.event_id IN (
        SELECT id
        FROM events e
        INNER JOIN stores s ON s.discord_id = e.discord_id
        WHERE e.game_id = {game.ID}
          AND e.format_id = {format.ID}
          AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
          {f'AND e.discord_id = {store.DiscordId}' if store else ''}
        ORDER BY event_date DESC
      )
      GROUP BY 1
      UNION
    )
    WHERE metagame_percent >= 0.02
    ORDER BY 4 DESC
    '''
    cur.execute(command)
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

#TODO: HAHAHAHAH this is awful, but it works. Maybe I can clean this up?
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
              AND reported = {False}
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
    {'INNER JOIN Formats f on f.id = e.format_id' if not format else ''}
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
    