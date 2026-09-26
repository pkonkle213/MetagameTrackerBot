from datetime import date
from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store


class EventStats(NamedTuple):
    event_date: date
    reported: int
    players: int
    percent_reported: float
    submitters: int
    percent_unique: float


async def GetAllEventsStats(
    store: Store, game: Game, format: Format
) -> list[EventStats]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(EventStats)) as cur,
    ):
        command = """
        WITH players AS (
        SELECT
                event_id,
                count(*) AS players
            FROM
                full_standings
            GROUP BY
                event_id
        ),
        submitters AS (
        SELECT
                event_id,
                count(DISTINCT submitter_id) AS submitters
            FROM
                archetype_submissions
            GROUP BY
                event_id
        )
        SELECT
            e.event_date,
            er.reported,
            p.players,
            round(100.0 * reported_percent, 2) AS percent_reported,
            a.submitters,
            round(100.0 * a.submitters / p.players, 2) AS percent_unique
        FROM
            players p
            INNER JOIN events_reported er ON er.id = p.event_id
            INNER JOIN submitters a ON p.event_id = a.event_id
            INNER JOIN events e ON e.id = p.event_id
            INNER JOIN games g ON g.id = e.game_id
            INNER JOIN formats f ON f.id = e.format_id
            INNER JOIN stores s ON s.discord_id = e.discord_id
        WHERE
            e.discord_id = %s
            AND g.id = %s
            AND f.id = %s
        ORDER BY
            p.event_id DESC
        """

        await cur.execute(command, [store.discord_id, game.id, format.id])
        rows = await cur.fetchall()
        return rows
