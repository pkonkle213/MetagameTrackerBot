from psycopg import AsyncConnection

from settings import DATABASE_URL


async def EnsureCommandInvocationsTable() -> None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        await cur.execute(
            """
            CREATE TABLE IF NOT EXISTS command_invocations (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id BIGINT NOT NULL,
                command_name TEXT NOT NULL,
                guild_id BIGINT,
                invoked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


async def LogCommandInvocation(
    user_id: int,
    command_name: str,
    guild_id: int | None,
) -> None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        await cur.execute(
            """
            INSERT INTO command_invocations (user_id, command_name, guild_id)
            VALUES (%s, %s, %s)
            """,
            (user_id, command_name, guild_id),
        )
