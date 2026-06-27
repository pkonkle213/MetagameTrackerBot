from psycopg.rows import class_row, scalar_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Game

def AddGameMap(
  discord_id:int,
  game_id:int,
  category_id:int
) -> int:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=scalar_row) as cur:
    command = f'''
    INSERT INTO game_category_maps
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

    print('AddGameMap command:', command)
    cur.execute(command)
    conn.commit()
    row = cur.fetchone()
    print('Row returned:', row)
    return row

def GetAllGames() -> list[Game]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(Game)) as cur:
    command = '''
    SELECT
      id,
      game_name
    FROM
      games
    ORDER BY
      game_name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows
    