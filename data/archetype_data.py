from datetime import date
from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row, scalar_row

from settings import DATABASE_URL
from tuple_conversions import Event, PlayerArchetype


async def PlayerInEvent(event: Event, player_name: str) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        SELECT
            e.id
        FROM
            events e
            INNER JOIN full_standings fs ON fs.event_id = e.id
        WHERE
            e.id = %s
            AND UPPER(fs.player_name) = UPPER(%s)
        """

        await cur.execute(command, [event.id, player_name])
        row = await cur.fetchone()
        return row is not None


async def BulkAddArchetypes(
    event: Event,
    archetypes: list[PlayerArchetype],
    user_id: int,
    user_name: str,
    user_discord_id: int,
    user_discord_name: str,
    is_submitter: bool = True,
) -> int:
    data_to_insert = [
        (
            event.id,
            archetype.player_name,
            archetype.archetype_played,
            user_id,
            user_name,
            user_discord_id,
            user_discord_name,
            is_submitter,
        )
        for archetype in archetypes
    ]

    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = """
        INSERT INTO archetype_submissions 
        (event_id,
        player_name,
        archetype_played,
        date_submitted,
        submitter_id,
        submitter_username,
        reported,
        submitter_discord_id,
        submitter_discord_name,
        is_submitter)
        VALUES
        (%s,
        %s,
        %s,
        NOW(),
        %s,
        %s,
        FALSE,
        %s,
        %s,
        %s)
        """

        await cur.executemany(command, data_to_insert)
        await conn.commit()
        return len(archetypes)


class UnknownArchetypes(NamedTuple):
    event_date: str
    event_name: str
    player_name: str


class OpponentArchetype(NamedTuple):
    round_number: int
    opponent_name: str
    archetype_played: str | None


async def GetOpponentArchetypes(
    event_id: int, user_id: int, discord_id: int
) -> list[OpponentArchetype]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(OpponentArchetype)) as cur,
    ):
        command = """
        SELECT
            fp.round_number,
            fp.opponent_name,
            ua.archetype_played
        FROM
            full_pairings fp
            INNER JOIN events e ON e.id = fp.event_id
            LEFT JOIN player_names pn
                ON upper(fp.player_name) = upper(pn.player_name)
                AND e.discord_id = pn.discord_id
            LEFT JOIN unique_archetypes ua
                ON ua.event_id = fp.event_id
                AND upper(ua.player_name) = upper(fp.opponent_name)
        WHERE
            fp.event_id = %s
            AND upper(fp.opponent_name) != 'BYE'
            AND pn.submitter_id = %s
            AND e.discord_id = %s
        ORDER BY
            fp.round_number
        """
        await cur.execute(command, [event_id, user_id, discord_id])
        return await cur.fetchall()


async def GetUnknownArchetypes(
    discord_id: int, game_id: int, format_id: int, start_date: date, end_date: date
) -> list[UnknownArchetypes]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(UnknownArchetypes)) as cur,
    ):
        command = """
        SELECT
            TO_CHAR(event_date, 'MM/DD/YYYY') as event_date,
            INITCAP(event_name) as event_name,
            INITCAP(player_name) as player_name
        FROM
            unknown_archetypes ua
        WHERE
            event_date BETWEEN %s AND %s
            AND game_id = %s
            AND format_id = %s
            AND discord_id = %s
        ORDER BY
            event_date desc,
            INITCAP(player_name)
        """

        await cur.execute(
            command, [start_date, end_date, game_id, format_id, discord_id]
        )
        rows = await cur.fetchall()
        return rows
