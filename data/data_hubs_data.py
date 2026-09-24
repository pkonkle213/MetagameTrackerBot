from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Event, Format, Game, Hub, HubsChannels, Store


async def GetPossibleHubs(store: Store, game: Game, format: Format) -> list[Hub]:
    """Gets all hubs related to a store, game, and format"""
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Hub)) as cur,
    ):
        command = """
        WITH criteria AS (
            SELECT
                %s as discord_id,
                %s as game_id,
                %s as format_id,
                %s as region_id
        )
        (
            SELECT
                hv.discord_id,
                hv.discord_name,
                hv.hub_name,
                hv.owner_id,
                hv.owner_name,
                hv.region_id,
                hv.game_lock,
                hv.format_lock,
                hv.is_paid,
                hv.invite
            FROM
                stores s
                INNER JOIN hubs_view hv ON hv.region_id = s.region_id
                INNER JOIN format_channel_maps fcm ON fcm.discord_id = hv.discord_id
                INNER JOIN criteria c ON s.discord_id = c.discord_id
                AND fcm.format_id = c.format_id
        )
        UNION
        (
            SELECT
                hv.discord_id,
                hv.discord_name,
                hv.hub_name,
                hv.owner_id,
                hv.owner_name,
                hv.region_id,
                hv.game_lock,
                hv.format_lock,
                hv.is_paid,
                hv.invite
            FROM
                stores s
                INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
                INNER JOIN hubs_view hv ON rcm.discord_id = hv.discord_id
                INNER JOIN criteria c ON s.discord_id = c.discord_id
                AND rcm.region_id = c.region_id
                AND hv.format_lock = c.format_id
        )
        LIMIT
            25
        """

        await cur.execute(
            command, [store.discord_id, game.id, format.id, store.region_id]
        )
        rows = await cur.fetchall()
        return rows


async def GetAllHubs(event: Event) -> list[HubsChannels]:
    """Gets all hub discordIds and channelIds for an event"""
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(HubsChannels)) as cur,
    ):
        command = """
        WITH
            selected_event AS (
                SELECT
                    *
                FROM
                    events
                WHERE
                    id = %s
            )
        (
            --Region Locked Hubs
            SELECT
                hv.discord_id,
                fcm.channel_id
            FROM
                selected_event e
                INNER JOIN stores s ON s.discord_id = e.discord_id
                INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = s.discord_id
                AND sah.format_id = e.format_id
                INNER JOIN hubs_view hv ON hv.discord_id = sah.hub_discord_id
                INNER JOIN format_channel_maps fcm ON fcm.format_id = e.format_id
                AND fcm.discord_id = hv.discord_id
        )
        UNION
        (
            --Format Locked Hubs
            SELECT
                hv.discord_id,
                rcm.channel_id
            FROM
                selected_event e
                INNER JOIN stores s ON e.discord_id = s.discord_id
                INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = s.discord_id
                AND sah.format_id = e.format_id
                INNER JOIN hubs_view hv ON hv.discord_id = sah.hub_discord_id
                INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
                AND rcm.discord_id = hv.discord_id
        )
        UNION
        (
            --Global Hubs
            SELECT
                hv.discord_id,
                fcm.channel_id
            FROM
                hubs_view hv
                INNER JOIN format_channel_maps fcm ON fcm.discord_id = hv.discord_id
                INNER JOIN selected_event e ON fcm.format_id = e.format_id
            WHERE
                region_id = 0
        )
        """

        await cur.execute(command, [event.id])
        return await cur.fetchall()
