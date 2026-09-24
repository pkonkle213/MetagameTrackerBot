from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL, DATAGUILDID
from tuple_conversions import Format, HubInvite, Store


async def GetAllHubInvites(store: Store, format: Format) -> list[HubInvite]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(HubInvite)) as cur,
    ):
        command = f"""
        (
            SELECT
            h.hub_name,
            h.invite
            FROM
            hubs_view h
            WHERE
            h.discord_id = {DATAGUILDID}
        )
        UNION ALL
        (
            SELECT
            h.hub_name,
            h.invite
            FROM
            hubs_view h
            INNER JOIN format_channel_maps fcm ON fcm.discord_id = h.discord_id
            WHERE
            h.region_id = {store.region_id}
            AND fcm.format_id = {format.id}
        )
        UNION ALL
        (
            SELECT
            h.hub_name,
            h.invite
            FROM
            hubs_view h
            INNER JOIN region_channel_maps rcm ON rcm.discord_id = h.discord_id
            WHERE
            rcm.region_id = {store.region_id}
            AND h.format_lock = {format.id}
        )
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows
