from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Store


class Details(NamedTuple):
    melee_client_id: str
    melee_client_secret: str


async def GetStoreMeleeInfo(store: Store) -> Details | None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Details)) as cur,
    ):
        command = """
        SELECT
            melee_client_id,
            melee_client_secret
        FROM
            stores
        WHERE
            discord_id = %s
        """

        await cur.execute(command, [store.discord_id])
        row = await cur.fetchone()
        return row
