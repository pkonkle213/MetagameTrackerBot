from custom_errors import KnownError
from settings import DATABASE_URL
from psycopg import AsyncConnection


async def GetHereCommands(
    is_store: bool,
    is_hub: bool,
    is_game: bool,
    is_format: bool,
    is_region: bool,
    user_is_submitter: bool,
    user_is_store: bool,
    user_is_paid: bool,
    store_is_paid: bool,
    hub_is_paid: bool,
):
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
          CASE
            WHEN command_group IS NULL THEN '/' || command_name
            ELSE '/' || command_group || ' ' || command_name
          END AS command_invoke,
          CASE
            WHEN requires_paid_user THEN 'Requires paid user'
            WHEN requires_paid_store THEN 'Requires paid store'
            WHEN requires_paid_hub THEN 'Requires paid hub'
            ELSE ' '
          END AS requirement
        FROM
          commands
        WHERE
            is_enabled = TRUE
            AND CASE
            WHEN {is_store} THEN store_use = TRUE
            WHEN {is_hub} THEN hub_use = TRUE
            ELSE TRUE END
            AND requires_game <= {is_game}
            AND requires_format <= {is_format}
            AND requires_mtstore_role <= {user_is_store}
            AND requires_mtsubmitter_role <= {user_is_submitter}
        ORDER BY
          sort_order
        """

        await cur.execute(command)  # ty:ignore[no-matching-overload]
        rows = await cur.fetchall()
        if len(rows) == 0:
            raise KnownError("No commands found for this channel")
        return rows


async def GetUserCommands(
    is_store: bool,
    is_hub: bool,
    is_game: bool,
    is_format: bool,
    is_region: bool,
    user_is_submitter: bool,
    user_is_store: bool,
    user_is_paid: bool,
    store_is_paid: bool,
    hub_is_paid: bool,
):
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
          CASE
            WHEN command_group IS NULL THEN '/' || command_name
            ELSE '/' || command_group || ' ' || command_name
          END AS command_invoke,
          description
        FROM
          commands
        WHERE
            is_enabled = TRUE
            AND CASE
            WHEN {is_store} THEN store_use = TRUE
            WHEN {is_hub} THEN hub_use = TRUE
            ELSE TRUE END
            AND requires_game <= {is_game}
            AND requires_format <= {is_format}
            AND requires_mtstore_role <= {user_is_store}
            AND requires_mtsubmitter_role <= {user_is_submitter}
            AND requires_paid_user <= {user_is_paid}
            AND requires_paid_store <= {store_is_paid}
            AND requires_paid_hub <= {hub_is_paid}
        ORDER BY
          sort_order
        """

        await cur.execute(command)  # ty:ignore[no-matching-overload]
        rows = await cur.fetchall()
        if len(rows) == 0:
            raise KnownError("No commands found for this channel")
        return rows
