from custom_errors import KnownError
from discord import Interaction, Guild, Member
from psycopg.rows import class_row, scalar_row
from settings import DATABASE_URL
from psycopg import AsyncConnection
from tuple_conversions import Store, Event, ChannelFormatMapping, Hub, Game, Format


async def UpdateHub(
    interaction: Interaction, discord_id: int, hub_name: str, hub_invite: str
) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        discord_command = f"""
        UPDATE discords
        SET discord_name = %s
            , owner_id = %s
            , owner_name = %s
        WHERE discord_id = %s
            """
        guild: Guild = interaction.guild
        owner: Member = guild.owner
        await cur.execute(
            discord_command, [guild.name, guild.owner_id, owner.name, discord_id]
        )
        await conn.commit()

        hub_command = f"""
        UPDATE hubs
        SET hub_name = %s
            , invite = %s
        WHERE discord_id = %s
        RETURNING discord_id
        """
        await cur.execute(hub_command, [hub_name, hub_invite, discord_id])
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise Exception(f"Unable to update hub: {discord_id}")
        return row


async def UpdateApprovedHubs(
    store: Store, game: Game | None, format: Format | None, hubs: list[int]
) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        delete_command = f"""
        DELETE FROM stores_approved_hubs
            WHERE store_discord_id = {store.discord_id}
            AND game_id = {game.id if game else "NULL"}
            AND format_id = {format.id if format else "NULL"}
            AND region_id = {store.region_id if store.region_id else "NULL"}
        """

        insert_command = f"""
        INSERT INTO stores_approved_hubs (store_discord_id, region_id, game_id, format_id, hub_discord_id)
        SELECT
            {store.discord_id},
            {store.region_id if store.region_id else "NULL"},
            {game.id if game else "NULL"},
            {format.id if format else "NULL"},
            unnest(%s::bigint[])
        """

        try:
            await cur.execute(delete_command)  # type: ignore[arg-type]
            await conn.commit()

            await cur.execute(insert_command, [hubs])  # type: ignore[arg-type]
            await conn.commit()
            return True
        except Exception as e:
            print("Error:", e)
            return False


async def UpdateStore(
    interaction: Interaction,
    store: Store,
    store_name: str,
    store_address: str,
    melee_id: str | None,
    melee_secret: str | None,
) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        discord_command = f"""
        UPDATE discords
        SET discord_name = %s
            , owner_id = %s
            , owner_name = %s
        WHERE discord_id = %s
            """
        guild: Guild = interaction.guild
        owner: Member = guild.owner
        await cur.execute(
            discord_command, [guild.name, guild.owner_id, owner.name, store.discord_id]
        )
        await conn.commit()

        store_command = f"""
        UPDATE stores
        SET store_name = %s
            , store_address = %s
            , melee_client_id = {"%s" if melee_id else "NULL"}
            , melee_client_secret = {"%s" if melee_secret else "NULL"}
        WHERE discord_id = %s
        RETURNING discord_id
        """

        criteria: list = [store_name, store_address]
        if melee_id:
            criteria.append(melee_id)
        if melee_secret:
            criteria.append(melee_secret)
        criteria.append(store.discord_id)

        await cur.execute(store_command, criteria)
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Unable to update store: {store.discord_id}")
        return row


async def DeleteStore(discord_id: int) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        DELETE FROM Stores
        WHERE discord_id = {discord_id}
        RETURNING TRUE
        """
        await cur.execute(command)
        await conn.commit()
        success = await cur.fetchone()
        return bool(success)


async def GetFormatMapByEvent(event: Event) -> ChannelFormatMapping:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(ChannelFormatMapping)) as cur,
    ):
        command = f"""
        SELECT
            discord_id,
            channel_id,
            format_id
        FROM
            format_channel_maps fcm
        WHERE
            fcm.discord_id = {event.discord_id}
            AND fcm.format_id= {event.format_id}
        """

        await cur.execute(command)
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Unable to find format map for event: {event.id}")
        return row


async def AddDiscord(
    discord_id: int, discord_name: str, owner_id: int, owner_name: str
) -> int | None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        INSERT INTO discords (discord_id, discord_name, owner_id, owner_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (discord_id) DO UPDATE
        SET discord_name = %s, owner_id = %s, owner_name = %s
        RETURNING discord_id
        """

        criteria = [discord_id, discord_name, owner_id, owner_name]
        await cur.execute(command, criteria + criteria[1:])
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Unable to add discord: {discord_id}")
        return row


async def AddStore(discord_id: int) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = f"""
        INSERT INTO stores (discord_id, used_for_data)
        VALUES (%s, TRUE)
        RETURNING discord_id
        """

        await cur.execute(command, [discord_id])
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Unable to add store: {discord_id}")
        return row


async def GetArchetypeFeed(discord_id: int, game_id: int) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        SELECT
            channel_id
        FROM
            archetype_feeds
        WHERE
            discord_id = %s
            AND game_id = %s
        """

        await cur.execute(command, [discord_id, game_id])
        row = await cur.fetchone()
        if not row:
            raise KnownError(
                f"Unable to find archetype submission feed for store: {discord_id}"
            )
        return row
