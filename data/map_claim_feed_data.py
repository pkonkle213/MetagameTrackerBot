from settings import DATABASE_URL
import psycopg

def AddClaimFeedMap(
  discord_id:int,
  channel_id:int,
  game_id:int
):
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO claimchannels (discord_id, channel_id, game_id)
    VALUES ({discord_id}, {channel_id}, {game_id})
    ON CONFLICT (discord_id, game_id) DO UPDATE
    SET channel_id = {channel_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row