import os
import psycopg2
from tuple_conversions import ConvertToGame

def AddGameMap(discord_id:int,
   game_id:int,
   category_id:int):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    INSERT INTO GameCategoryMaps
    (discord_id,
    game_id,
    category_id)
    VALUES
    ({discord_id},
    {game_id},
    {category_id})
    ON CONFLICT (discord_id, category_id) DO UPDATE
    SET game_id = {game_id}
    RETURNING *
    '''
    
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    return row

def GetAllGames():
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = '''
    SELECT id, name, hasFormats
    FROM Games
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return [ConvertToGame(row) for row in rows]
    