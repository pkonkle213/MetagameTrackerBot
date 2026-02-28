import os
import psycopg
from psycopg.rows import class_row
from tuple_conversions import Format, Game

def AddFormatMap(
  discord_id:int,
  format_id:int,
  channel_id:int
):
  conn = psycopg.connect(os.environ['DATABASE_URL'])
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

def GetFormatsByGameId(game:Game) -> list[Format]:
  conn = psycopg.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor(row_factory=class_row(Format)) as cur:
    command = f'''
    SELECT id, name, last_ban_update, is_limited
    FROM formats
    WHERE game_id = {game.GameId}
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows