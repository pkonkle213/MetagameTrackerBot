from typing import Any
from settings import DATABASE_URL
import psycopg2

def GetDataChannels(data_guild_id:int) -> list[tuple[Any,...]]:
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      channel_id,
      category_id
    FROM
      formatchannelmaps fcm
      INNER JOIN formats f ON fcm.format_id = f.id
      INNER JOIN Games g ON g.id = f.game_id
      INNER JOIN gamecategorymaps gcm ON (
        gcm.game_id = g.id
        AND gcm.discord_id = fcm.discord_id
      )
    WHERE fcm.discord_id = {data_guild_id}
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows