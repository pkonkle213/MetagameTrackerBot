from psycopg import AsyncConnection

from settings import DATABASE_URL


async def ReplaceInventory(rows: list[tuple[int, str, str]]) -> int:
    """Atomically replace all inventory rows and return the inserted row count."""
    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory (
                    quantity INTEGER NOT NULL CHECK (quantity >= 0),
                    card_name TEXT NOT NULL,
                    card_edition TEXT NOT NULL
                )
                """
            )
            await cur.execute("DELETE FROM inventory")
            await cur.executemany(
                """
                INSERT INTO inventory (quantity, card_name, card_edition)
                VALUES (%s, %s, %s)
                """,
                rows,
            )
        await conn.commit()
    return len(rows)
