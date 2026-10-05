from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import scalar_row

from settings import DATABASE_URL, DATAGUILDID


class DataGuildChannels(NamedTuple):
    game_id: int
    format_id: int
    channel_id: int


async def GetDataChannels() -> list[DataGuildChannels]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        SELECT
            g.id as game_id,
            f.id as format_id,
            channel_id
        FROM
            format_channel_maps fcm
            INNER JOIN formats f ON fcm.format_id = f.id
            INNER JOIN games g ON g.id = f.game_id
            INNER JOIN game_category_maps gcm ON (
                gcm.game_id = g.id
                AND gcm.discord_id = fcm.discord_id
            )
        WHERE fcm.discord_id = %s
        """

        criteria = [DATAGUILDID]
        await cur.execute(command, criteria)
        rows = await cur.fetchall()
        return rows
