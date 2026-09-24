from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row

from custom_errors import KnownError
from settings import DATABASE_URL


class MappedClaimFeed(NamedTuple):
    discord_id: int
    channel_id: int
    game_id: int


async def AddClaimFeedMap(
    discord_id: int, channel_id: int, game_id: int
) -> MappedClaimFeed:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(MappedClaimFeed)) as cur,
    ):
        command = """
        INSERT INTO archetype_feeds (discord_id, channel_id, game_id)
        VALUES (%s, %s, %s)
        RETURNING *
        """

        await cur.execute(command, [discord_id, channel_id, game_id])
        await conn.commit()
        row = await cur.fetchone()

        if not row:
            raise KnownError("Unable to map channel to archetype feed")
        return row
