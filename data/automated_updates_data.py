from typing import NamedTuple
from psycopg.rows import class_row
from settings import DATABASE_URL
import psycopg

class DataGuildChannels(NamedTuple):
  channel_id:int
  category_id: int

def GetDataChannels(data_guild_id:int) -> list[DataGuildChannels]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(DataGuildChannels)) as cur:
    command = '''
    SELECT
      channel_id,
      category_id
    FROM
      format_channel_maps fcm
      INNER JOIN formats f ON fcm.format_id = f.id
      INNER JOIN Games g ON g.id = f.game_id
      INNER JOIN game_category_maps gcm ON (
        gcm.game_id = g.id
        AND gcm.discord_id = fcm.discord_id
      )
    WHERE fcm.discord_id = %s
    '''

    criteria = [data_guild_id]
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return rows