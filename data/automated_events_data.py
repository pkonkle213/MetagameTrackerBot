from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL


class StaleEvents(NamedTuple):
    discord_id: int
    event_id: int
    is_complete: bool
    game_id: int
    format_id: int
    channel_id: int
    has_unknown: bool


async def ThreeDayOldEvents() -> list[StaleEvents]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(StaleEvents)) as cur,
    ):
        command = """
        SELECT
            e.discord_id,
            e.id as event_id,
            e.is_complete,
            gm.game_id AS game_id,
            fm.format_id AS format_id,
            fm.channel_id,
            SUM(er.reported) < SUM(er.total_attended) AS has_unknown
        FROM
            events_reported er
            INNER JOIN events e ON e.id = er.id
            INNER JOIN game_category_maps gm ON gm.game_id = e.game_id
            AND gm.discord_id = e.discord_id
            INNER JOIN format_channel_maps fm ON fm.format_id = e.format_id
            AND fm.discord_id = e.discord_id
        WHERE
            e.event_date = NOW()::date - INTERVAL '3 days'
        GROUP BY
            e.discord_id,
            e.id,
            gm.game_id,
            gm.category_id,
            fm.format_id,
            fm.channel_id
        """

        await cur.execute(command)
        rows = await cur.fetchall()
        return rows
