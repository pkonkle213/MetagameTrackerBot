from settings import DATABASE_URL
from psycopg.rows import scalar_row
import psycopg
from tuple_conversions import Standing, Pairing


async def InsertPairing(
    event_id: int, pairing: Pairing, submitter_id: int
) -> int | None:
    try:
        async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
            async with conn.cursor(row_factory=scalar_row) as cur:
                command = """
                INSERT INTO pairings
                (event_id,
                round_number,
                player1_game_wins,
                player2_game_wins,
                player1_name,
                player2_name,
                submitter_id)
                VALUES (%s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s)
                RETURNING event_id
                """

                criteria = (
                    event_id,
                    pairing.round_number,
                    pairing.player1_game_wins,
                    pairing.player2_game_wins,
                    pairing.player1_name,
                    pairing.player2_name,
                    submitter_id,
                )
                await cur.execute(command, criteria)
                row = await cur.fetchone()
                return row
    except psycopg.errors.UniqueViolation:
        return None


async def CheckPairings(
    event_id: int, round_number: int, p1name: str, p2name: str
) -> bool:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            command = """
            SELECT
                *
            FROM
                pairings
            WHERE
                event_id = %s
                AND round_number = %s
                AND (
                    UPPER(player1_name) = UPPER(%s)
                    OR UPPER(player1_name) = UPPER(%s)
                    OR UPPER(player2_name) = UPPER(%s)
                    OR UPPER(player2_name) = UPPER(%s)
                )
            """

            criteria = [event_id, round_number, p1name, p2name, p2name, p1name]
            await cur.execute(command, criteria)
            row = await cur.fetchone()
            return row is None


async def InsertStanding(
    event_id: int, player: Standing, submitter_id: int
) -> int | None:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            try:
                command = """
                INSERT INTO standings
                (event_id,
                player_name,
                wins,
                losses,
                draws,
                submitter_id)
                VALUES
                (%s,
                %s,
                %s,
                %s,
                %s,
                %s)
                RETURNING event_id
                """

                criteria = [
                    event_id,
                    player.player_name,
                    player.wins,
                    player.losses,
                    player.draws,
                    submitter_id,
                ]
                await cur.execute(command, criteria)

                await conn.commit()
                row = await cur.fetchone()
                return row[0] if row else None
            except psycopg.errors.UniqueViolation:
                return None
