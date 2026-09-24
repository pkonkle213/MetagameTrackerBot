from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Hub, Region


async def GetRegions() -> list[Region]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Region)) as cur,
    ):
        command = """
        SELECT
            id,
            region_name
        FROM
            regions
        ORDER BY
            region_name
        """

        await cur.execute(command)
        rows = await cur.fetchall()
        return rows


async def GetHub(discord_id: int) -> Hub:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Hub)) as cur,
    ):
        command = """
        SELECT
            *
        FROM
            hubs_view
        WHERE
            discord_id = %s
        """

        await cur.execute(command, [discord_id])

        row = await cur.fetchone()
        if not row:
            raise KnownError("No hub found")
        return row


class RegionMap(NamedTuple):
    discord_id: int
    channel_id: int
    region_id: int


async def AddRegionMap(hub: Hub, channel_id: int, region: Region) -> RegionMap:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(RegionMap)) as cur,
    ):
        command = f"""
        INSERT INTO region_channel_maps (discord_id, channel_id, region_id)
        VALUES ({hub.discord_id}, {channel_id}, {region.id})
        ON CONFLICT (discord_id, channel_id) DO UPDATE
        SET region_id = {region.id}
        RETURNING *
        """

        await cur.execute(command)  # type: ignore[arg-type]
        await conn.commit()
        row = await cur.fetchone()
        if not row:
            raise KnownError("Failed to map region. Please try again later.")
        return row
