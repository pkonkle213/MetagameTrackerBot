from typing import Any, NamedTuple

from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation
from psycopg.rows import class_row, scalar_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store


class Word(NamedTuple):
    id: int
    banned_word: str


async def AddWord(word: str) -> Word | None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Word)) as cur,
    ):
        try:
            criteria = [word]
            command = """
            INSERT INTO BadWords (badword)
            VALUES (%s)
            RETURNING id, banned_word
            """

            await cur.execute(command, criteria)
            await conn.commit()
            row = await cur.fetchone()
            if not row:
                raise KnownError("Unable to add word")
            return row
        except UniqueViolation:
            return None


async def GetWord(word: str) -> Word:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Word)) as cur,
    ):
        command = """
        SELECT
            id,
            banned_word
        FROM
            banned_words
        WHERE
            banned_word = %s
        """

        criteria = [word]
        await cur.execute(command, criteria)
        row = await cur.fetchone()

        if not row:
            raise KnownError("Unable to find the word")
        return row


async def MatchDisabledArchetypes(discord_id: int, user_id: int) -> int:
    days = 30
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        SELECT
            COUNT(*)
        FROM
            archetype_submissions asu
            INNER JOIN events e ON e.id = asu.event_id
        WHERE
            e.discord_id = %s
            AND asu.submitter_id = %s
            AND asu.reported = TRUE
            AND e.event_date BETWEEN current_date - %s AND current_date
        """

        criteria = [discord_id, user_id, days]
        await cur.execute(command, criteria)
        count = await cur.fetchone()
        return count if count else 0


async def DisableMatchingWords(discord_id: int, word: str) -> list[Any]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        word_inject = "%" + word + "%"
        command = """
        UPDATE archetype_submissions
        SET reported = True
        WHERE event_id IN (
            SELECT id
            FROM events
            WHERE discord_id = %s
        )
        AND archetype_played LIKE %s
        RETURNING *
        """

        criteria = [discord_id, word_inject]
        await cur.execute(command, criteria)
        await conn.commit()
        row = await cur.fetchall()
        return row


async def AddBadWordBridge(discord_id: int, word_id: int) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = """
        INSERT INTO banned_words_stores (discord_id, banned_word_id)
        VALUES (%s, %s)
        RETURNING *
        """

        criteria = [discord_id, word_id]
        await cur.execute(command, criteria)
        await conn.commit()
        row = await cur.fetchone()
        return bool(row)


async def CheckStoreBannedWords(discord_id: int, archetype: str) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = """
        SELECT
            *
        FROM
            banned_words b
            INNER JOIN banned_words_stores bs ON b.id = bs.banned_word_id
        WHERE
            bs.discord_id = %s
            AND POSITION(banned_word IN %s) > 0
        """

        criteria = [discord_id, archetype]
        await cur.execute(command, criteria)
        rows = await cur.fetchall()
        return len(rows)


# TODO: Make more concrete
async def GetOffenders(game: Game, format: Format, store: Store) -> list[Any]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = """
        SELECT 
            asu.date_submitted::date as date_submitted,
            asu.submitter_username,
            asu.submitter_id,
            e.event_date,
            {"g.game_name," if not game else ""}
            {"f.format_name," if not format else ""}
            asu.player_name,
            asu.archetype_played
        FROM archetype_submissions asu
            INNER JOIN Events e on e.id = asu.event_id
            INNER JOIN Games c on c.id = e.game_id
            INNER JOIN Formats f on f.id = e.format_id
        WHERE asu.reported = TRUE
            AND e.discord_id = %s
            {f"AND e.game_id = %s" if game else ""}
            {f"AND e.format_id = %s" if format else ""}
        ORDER BY asu.date_submitted DESC
        """

        await cur.execute(command, [store.discord_id, game.id, format.id])
        rows = await cur.fetchall()
        return rows
