from custom_errors import KnownError
from psycopg.rows import scalar_row
from settings import DATABASE_URL
import psycopg
from tuple_conversions import Store, Game, Format


def UpdatePlayerNamesInStandings(
    store: Store, game: Game, format: Format, old_name: str, new_name: str
) -> int:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor() as cur:
        command = f"""
        UPDATE standings
        SET player_name = '{new_name}'
        WHERE event_id IN (
            SELECT
                id
            FROM
                events
            WHERE
                discord_id = {store.discord_id}
                AND game_id = {game.id}
                AND format_id = {format.id}
        )
            AND UPPER(player_name) = upper('{old_name}')
        RETURNING *
        """

        try:
            cur.execute(command)
            conn.commit()
            return cur.rowcount
        except psycopg.errors.UniqueViolation as e:
             raise KnownError(f"Unable to update player names in standings: `{old_name}` to `{new_name}`")


def UpdatePlayerNamesInPairings(
    store: Store, game: Game, format: Format, old_name: str, new_name: str
) -> int:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=scalar_row) as cur:
        command = f"""
        UPDATE pairings
        SET player1_name = CASE WHEN upper(player1_name) = upper('{old_name}') THEN '{new_name}' ELSE player1_name END,
            player2_name = CASE WHEN upper(player2_name) = upper('{old_name}') THEN '{new_name}' ELSE player2_name END
        WHERE event_id IN (
            SELECT
                id
            FROM
                events
            WHERE
                discord_id = {store.discord_id}
                AND game_id = {game.id}
                AND format_id = {format.id}
        )
            AND (UPPER(player1_name) = upper('{old_name}') OR upper(player2_name) = upper('{old_name}'))
        RETURNING *
        """

        try:
            cur.execute(command)
            conn.commit()
            return cur.rowcount
        except psycopg.errors.UniqueViolation as e:
            raise KnownError(f"Unable to update player names in pairings: `{old_name}` to `{new_name}`")


def UpdatePlayerNameInArchetypes(
    store: Store, game: Game, format: Format, old_name: str, new_name: str
) -> int:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor() as cur:
        command = f"""
        UPDATE archetype_submissions
        SET player_name = '{new_name}'
        WHERE event_id IN (
            SELECT
                id
            FROM
                events
            WHERE
                discord_id = {store.discord_id}
                AND game_id = {game.id}
                AND format_id = {format.id}
        )
            AND UPPER(player_name) = upper('{old_name}')
        RETURNING *
        """

        try:
            cur.execute(command)
            conn.commit()
            return cur.rowcount
        except psycopg.errors.UniqueViolation as e:
             raise KnownError(f"Unable to update player names in archetypes: `{old_name}` to `{new_name}`")