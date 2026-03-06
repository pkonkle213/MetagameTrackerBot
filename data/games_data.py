from psycopg.rows import class_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Game

def AddGameMap(
  discord_id:int,
  game_id:int,
  category_id:int
):
  conn = psycopg.connect(DATABASE_URL)
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

def GetAllGames() -> list[Game]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Game)) as cur:
    command = '''
    SELECT id, name
    FROM Games
    ORDER BY name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows
    