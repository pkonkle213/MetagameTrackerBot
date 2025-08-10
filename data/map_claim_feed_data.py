import os
import psycopg2

def AddClaimFeedMap(discord_id, channel_id, game_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO claimreportchannels (discord_id, channel_id, game_id)
    VALUES ({discord_id}, {channel_id}, {game_id})
    ON CONFLICT (discord_id, game_id) DO UPDATE
    SET channel_id = {channel_id}
    RETURNING *
    '''
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row