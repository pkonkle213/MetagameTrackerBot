import psycopg2
from models.format import Format
from models.game import Game
from settings import DATABASE_URL

def AddFormatMap(discord_id:int,
  format_id:int,
  channel_id:int):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO FormatChannelMaps
      (discord_id,
      format_id,
      channel_id)
    VALUES
      ({discord_id},
      {format_id},
      {channel_id})
    ON CONFLICT (discord_id, channel_id) DO UPDATE
    SET format_id = {format_id}
    RETURNING discord_id, format_id, channel_id
    '''
    
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    print('Object returend by AddFormatMap:', row)
    return row

def GetFormatsByGameId(game:Game):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT id, name, last_ban_update, is_limited
    FROM formats
    WHERE game_id = {game.ID}
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [Format(row[0], row[1], row[2], row[3]) for row in rows] if rows else None