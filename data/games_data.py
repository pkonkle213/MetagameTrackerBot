from psycopg import AsyncConnection
from psycopg.rows import class_row, scalar_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Game


async def AddGameMap(discord_id: int, game_id: int, category_id: int) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = f"""
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
        """

        await cur.execute(command)  # type: ignore[arg-type]
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise KnownError("Unable to add game map")
        return row


async def GetAllGames() -> list[Game]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Game)) as cur,
    ):
        command = """
        SELECT
            id,
            game_name
        FROM
            games
        ORDER BY
            game_name
        """
        await cur.execute(command)
        rows = await cur.fetchall()
        return rows
