from datetime import date, timedelta

from psycopg import AsyncConnection
from psycopg.rows import class_row, scalar_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Format, Game, LastArchetype, Store, TopDeck


async def GetWinPercentage(
    user_id: int, store: Store, game: Game, format: Format
) -> float:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        SELECT
            ROUND(100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)), 2) AS win_percentage
        FROM
            full_standings fs
            INNER JOIN events e ON fs.event_id = e.id
            INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name) AND pn.discord_id = e.discord_id
        WHERE
            e.discord_id = %s
            AND pn.submitter_id = %s
            AND e.event_date >= CURRENT_DATE - INTERVAL '1 year'
            AND e.format_id = %s
            AND e.game_id = %s
        """

        await cur.execute(
            command,
            [
                store.discord_id,
                user_id,
                format.id,
                game.id,
            ],
        )

        row = await cur.fetchone()
        if not row:
            raise KnownError("This person has not played any games in this format")
        return row


async def GetLastArchetype(
    user_id: int, store: Store, game: Game, format: Format
) -> LastArchetype:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(LastArchetype)) as cur,
    ):
        command = """
        SELECT
            TO_CHAR(e.event_date,'MM/DD') as event_date,
            INITCAP(archetype_played) as archetype_played
        FROM
            full_standings fs
            INNER JOIN events e ON fs.event_id = e.id
            INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name) AND pn.discord_id = e.discord_id
            INNER JOIN unique_archetypes ua ON e.id = ua.event_id AND UPPER(ua.player_name) = UPPER(fs.player_name)
        WHERE
            e.discord_id = %s
            AND e.event_date < CURRENT_DATE
            AND pn.submitter_id = %s
            AND e.format_id = %s
            AND e.game_id = %s
        ORDER BY e.event_date DESC
        LIMIT 1
        """

        await cur.execute(command, [store.discord_id, user_id, format.id, game.id])
        row = await cur.fetchone()
        if not row:
            raise KnownError("This person has not played any games in this format")
        return row


async def GetMostPlayed(
    user_id: int, store: Store, game: Game, format: Format
) -> list[TopDeck]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(TopDeck)) as cur,
    ):
        command = """
        WITH
            results AS (
            SELECT
                INITCAP(archetype_played) AS archetype_played,
                wins,
                losses,
                draws
            FROM
                full_standings fs
                INNER JOIN events e ON fs.event_id = e.id
                INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name)
                AND pn.discord_id = e.discord_id
                INNER JOIN unique_archetypes ua ON e.id = ua.event_id
                AND UPPER(ua.player_name) = UPPER(fs.player_name)
            WHERE
                e.discord_id = %s
                AND pn.submitter_id = %s
                AND e.format_id = %s
                AND e.game_id = %s
                AND e.event_date >= CURRENT_DATE - INTERVAL '1 year'
            )
            SELECT 
                archetype_played,
                ROUND(
                    100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)),
                    2
                ) AS win_percentage,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS chance_played
            FROM
                results
            GROUP BY
                archetype_played
            ORDER BY
                3 DESC,
                1
            LIMIT
                3
        """

        await cur.execute(command, [store.discord_id, user_id, format.id, game.id])
        rows = await cur.fetchall()
        return rows
