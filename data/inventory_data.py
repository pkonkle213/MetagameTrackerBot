from psycopg import AsyncConnection

from settings import DATABASE_URL


async def ReplaceInventory(rows: list[tuple[int, str, str]]) -> int:
    """Atomically replace all inventory rows and return the inserted row count."""
    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory (
                    inventory_id BIGSERIAL PRIMARY KEY,
                    quantity INTEGER NOT NULL CHECK (quantity >= 0),
                    card_name TEXT NOT NULL,
                    card_edition TEXT NOT NULL
                )
                """
            )
            await cur.execute(
                "ALTER TABLE inventory ADD COLUMN IF NOT EXISTS inventory_id BIGSERIAL"
            )
            await cur.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS inventory_inventory_id_uq "
                "ON inventory (inventory_id)"
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


async def GetInventoryForNames(names: list[str]) -> list[tuple[int, str, str, int]]:
    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT inventory_id, card_name, card_edition, quantity
                FROM inventory
                WHERE lower(card_name) = ANY(%s)
                ORDER BY lower(card_name), card_edition, inventory_id
                """,
                [[name.casefold() for name in names]],
            )
            return await cur.fetchall()


async def DeductInventory(rows: list[tuple[int, int]]) -> None:
    """Deduct from locked inventory row IDs; roll back if any row changed."""
    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "LOCK TABLE inventory IN SHARE ROW EXCLUSIVE MODE"
            )
            for inventory_id, quantity in rows:
                await cur.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity - %s
                    WHERE inventory_id = %s AND quantity >= %s
                    """,
                    [quantity, inventory_id, quantity],
                )
                if cur.rowcount != 1:
                    raise RuntimeError(
                        "Inventory changed while preparing the trade; no stock was deducted."
                    )
        await conn.commit()
