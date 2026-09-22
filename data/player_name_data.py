from psycopg.rows import class_row
from typing import NamedTuple
from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store


class PlayerDetails(NamedTuple):
    player_name: str
    archetypes: list[str]


def GetArchetypeModalDetails(user_id: int, game: Game, format: Format) -> PlayerDetails:
    """Get's a player's name and their 10 top played archetypes"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(PlayerDetails)) as cur:
        command = """
        WITH
            criteria AS (
                SELECT
                    %s AS user_id,
                    %s AS game_id,
                    %s AS format_id
            ),
            name AS (
                SELECT
                    player_name
                FROM
                    player_names pn
                    INNER JOIN criteria c ON c.user_id = pn.submitter_id
                GROUP BY
                    player_name
                ORDER BY
                    COUNT(*) DESC
                LIMIT
                    1
            ),
            archetypes AS (
                SELECT
                    INITCAP(pn.player_name) AS player_name,
                    INITCAP(ua.archetype_played) AS archetype_played
                FROM
                    unique_archetypes ua
                    INNER JOIN events e ON e.id = ua.event_id
                    INNER JOIN player_names pn ON e.discord_id = pn.discord_id
                    AND upper(ua.player_name) = upper(pn.player_name)
                    INNER JOIN criteria c ON c.user_id = pn.submitter_id
                    AND c.game_id = e.game_id
                    AND c.format_id = e.format_id
                GROUP BY
                    INITCAP(pn.player_name),
                    INITCAP(ua.archetype_played)
                ORDER BY
                    COUNT(*) DESC
                LIMIT
                    10
            )
        SELECT
            n.player_name,
            ARRAY_AGG(a.archetype_played)
        FROM
            name n
            INNER JOIN archetypes a ON a.player_name = n.player_name
        GROUP BY
            n.player_name
        """

        criteria = [user_id, game.id, format.id]
        cur.execute(command, criteria)
        row = cur.fetchone()
        if not row:
            return PlayerDetails("", [])
        return row


def GetUserName(userId: int) -> str:
    """Gets the user's name from the database"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor() as cur:
        command = """
        SELECT
            player_name
        FROM
            player_names
        WHERE
            submitter_id = %s
        GROUP BY
            player_name
        ORDER BY
            COUNT(*) DESC
        LIMIT 1
        """

        criteria = [userId]
        cur.execute(command, criteria)
        row = cur.fetchone()
        return row[0] if row else ""
