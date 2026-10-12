from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Pairing


async def GetEventByRounds(event_id: int) -> list[Pairing]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Pairing)) as cur,
    ):
        command = """
        SELECT
            round_number,
            player1_name,
            player2_name,
            player1_game_wins,
            player2_game_wins
        FROM
            pairings
        WHERE
            event_id = %s
        ORDER BY
            round_number DESC
        """

        await cur.execute(command, [event_id])
        rows = await cur.fetchall()
        return rows
