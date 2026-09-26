from psycopg import AsyncConnection
from psycopg.rows import scalar_row

from custom_errors import KnownError
from settings import DATABASE_URL


async def GetEventReportedPercentage(event_id: int) -> float:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        SELECT
        COUNT(
            CASE
            WHEN archetype_played IS NOT NULL THEN 1
            END
        ) / SUM(count(*)) OVER () AS percentage
        FROM
        full_standings fp
        LEFT OUTER JOIN unique_archetypes ua ON ua.event_id = fp.event_id
        AND UPPER(ua.player_name) = UPPER(fp.player_name)
        WHERE
        fp.event_id = %s
        """

        await cur.execute(command, [event_id])
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Unable to get event {event_id}'s reported percentage")
        return row[0]


async def UpdateEvent(event_id: int) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = """
        UPDATE events
        SET last_update = last_update + 1
        WHERE id = %s
        RETURNING id
        """

        await cur.execute(command, [event_id])
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Unable to update event {event_id}")
        return row[0]
