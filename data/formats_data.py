import os
import psycopg2

from tuple_conversions import ConvertToFormat

def AddFormatMap(discord_id:int,
   format_id:int,
   channel_id:int):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
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
    RETURNING *
    '''
    
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

def GetFormatsByGameId(game):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT id, name, last_ban_update, is_limited
    FROM formats
    WHERE game_id = {game.GameId}
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [ConvertToFormat(row) for row in rows] if rows else None