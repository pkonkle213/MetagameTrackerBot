from psycopg import AsyncConnection
from psycopg.rows import class_row, scalar_row

from settings import DATABASE_URL
from tuple_conversions import Format, Game


async def AddFormatMap(discord_id: int, format_id: int, channel_id: int) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
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
        """

        await cur.execute(command)  # type: ignore[arg-type]
        await conn.commit()
        row = await cur.fetchone()
        return bool(row)


async def GetFormatsByGameId(game: Game) -> list[Format]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Format)) as cur,
    ):
        command = """
        SELECT
            id,
            format_name,
            last_ban_update,
            is_limited
        FROM
            formats
        WHERE
            game_id = 
        ORDER BY
            format_name
        """
        await cur.execute(command, [game.id])
        rows = await cur.fetchall()
        return rows
