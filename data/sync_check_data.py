from psycopg.rows import scalar_row
from settings import FIVE6STOREID, DATABASE_URL
from psycopg import AsyncConnection


async def GetFive6Users() -> list[int]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = f"""
        SELECT DISTINCT submitter_id
        FROM player_names
        WHERE discord_id = %s
        """

        await cur.execute(command, [FIVE6STOREID])
        results = await cur.fetchall()
        return results


async def GetStores(paid: bool = False) -> list[int]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = f"""
        SELECT
            discord_id
        FROM
            stores_view
        {f"WHERE is_paid = true" if paid else ""}
        """

        await cur.execute(command)
        results = await cur.fetchall()
        return results


async def GetHubs(paid: bool = False) -> list[int]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = f"""
        SELECT
            discord_id
        FROM
            hubs_view
        {f"WHERE is_paid = true" if paid else ""}
        """

        await cur.execute(command)
        results = await cur.fetchall()
        return results
