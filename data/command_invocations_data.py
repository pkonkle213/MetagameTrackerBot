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
                category_id BIGINT,
                channel_id BIGINT,
                has_mt_submitter_role BOOLEAN NOT NULL DEFAULT FALSE,
                has_mt_store_role BOOLEAN NOT NULL DEFAULT FALSE,
                invoked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await cur.execute(
            """
            ALTER TABLE command_invocations
                ADD COLUMN IF NOT EXISTS has_mt_submitter_role
                    BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS has_mt_store_role
                    BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS category_id BIGINT,
                ADD COLUMN IF NOT EXISTS channel_id BIGINT
            """
        )


async def LogCommandInvocation(
    user_id: int,
    command_name: str,
    guild_id: int | None,
    category_id: int | None,
    channel_id: int | None,
    has_mt_submitter_role: bool,
    has_mt_store_role: bool,
) -> None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        await cur.execute(
            """
            INSERT INTO command_invocations (
                user_id,
                command_name,
                guild_id,
                category_id,
                channel_id,
                has_mt_submitter_role,
                has_mt_store_role
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                command_name,
                guild_id,
                category_id,
                channel_id,
                has_mt_submitter_role,
                has_mt_store_role,
            ),
        )
