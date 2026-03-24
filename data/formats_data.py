from settings import DATABASE_URL
import psycopg
from psycopg.rows import class_row
from tuple_conversions import Format, Game

def AddFormatMap(
  discord_id:int,
  format_id:int,
  channel_id:int
):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO format_channel_maps
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
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Format)) as cur:
    command = f'''
    SELECT
      id as format_id,
      format_name,
      last_ban_update,
      is_limited
    FROM
      formats
    WHERE
      game_id = {game.id}
    ORDER BY
      format_name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows