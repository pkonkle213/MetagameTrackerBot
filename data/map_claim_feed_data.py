from typing import NamedTuple

from psycopg.rows import class_row
from custom_errors import KnownError
from settings import DATABASE_URL
import psycopg

class MappedClaimFeed(NamedTuple):
  discord_id: int
  channel_id: int
  game_id: int

def AddClaimFeedMap(
  discord_id:int,
  channel_id:int,
  game_id:int
) -> MappedClaimFeed:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(MappedClaimFeed)) as cur:
    command = f'''
    INSERT INTO archetype_feeds (discord_id, channel_id, game_id)
    VALUES ({discord_id}, {channel_id}, {game_id})
    ON CONFLICT (discord_id, game_id) DO UPDATE
    SET channel_id = {channel_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    
    if not row:
      raise KnownError('Unable to map channel to archetype feed')
    return row