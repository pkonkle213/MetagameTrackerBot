from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Card, Deck, Event


async def GetDecks(event: Event) -> list[Deck]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Deck)) as cur,
    ):
        command = """
        SELECT
            d.deck_id as id,
            INITCAP(COALESCE(ua.archetype_played, 'Unknown')) AS archetype_played,
            fs.wins,
            fs.losses,
            fs.draws
        FROM
            decks_view d
            INNER JOIN full_standings fs ON fs.event_id = d.event_id
            AND upper(fs.player_name) = upper(d.player_name)
            LEFT JOIN unique_archetypes ua ON ua.event_id = d.event_id
            AND upper(ua.player_name) = upper(d.player_name)
        WHERE
            d.event_id = %s
        ORDER BY
            fs.wins DESC,
            fs.draws DESC,
            fs.losses DESC
        """

        await cur.execute(command, [event.id])
        rows = await cur.fetchall()
        return rows


async def GetDecklists(event: Event) -> list[Card]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Card)) as cur,
    ):
        command = """
        SELECT
            deck_id,
            quantity,
            card_name,
            is_mainboard
        FROM
            decklists
        WHERE
            deck_id IN (
            SELECT
            id
            FROM
            decks
            WHERE
            event_id = %s
            )
        ORDER BY
            deck_id,
            is_mainboard DESC,
            card_name
        """

        await cur.execute(command, [event.id])
        rows = await cur.fetchall()

        return rows
