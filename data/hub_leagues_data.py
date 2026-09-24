from psycopg import AsyncConnection
from psycopg.rows import class_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Hub, Store


async def GetAllowedStores(hub: Hub, game: Game, format: Format) -> list[Store]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Store)) as cur,
    ):
        command = """
        SELECT
            sv.discord_id
            , sv.discord_name
            , sv.owner_id
            , sv.owner_name
            , sv.store_name
            , sv.store_address
            , sv.used_for_data
            , sv.region_id
            , sv.is_paid
        FROM
            stores_approved_hubs sah
            INNER JOIN stores_view sv ON sv.discord_id = sah.store_discord_id
        WHERE
            sah.hub_discord_id = %s
            AND sah.game_id = %s
            AND sah.format_id = %s
        LIMIT 25
        """

        await cur.execute(command, [hub.discord_id, game.id, format.id])
        await conn.commit()

        rows = await cur.fetchall()
        if len(rows) == 0:
            raise KnownError("No supported stores found")
        return rows


async def UpdateAssociatedStores(league_id: int, selected_store_ids: list[int]) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        delete_command = """
        DELETE FROM hub_league_stores
        WHERE league_id = %s
        """

        add_command = """
        INSERT INTO hub_league_stores (league_id, store_discord_id)
        SELECT
            %s,
            unnest(%s::bigint[])
        """

        try:
            await cur.execute(delete_command, [league_id])
            await conn.commit()

            await cur.execute(add_command, [league_id, selected_store_ids])
            await conn.commit()
            return True
        except Exception as e:
            print("Error:", e)
            return False
