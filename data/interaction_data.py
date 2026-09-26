from datetime import date
from typing import NamedTuple

from discord import DMChannel, GroupChannel, Interaction
from psycopg import AsyncConnection
from psycopg.rows import kwargs_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Hub, Region, Store


class InteractionRow(NamedTuple):
    store: Store | None
    hub: Hub | None
    game: Game | None
    format: Format | None
    region: Region | None


def interaction_row(
    *,
    store_discord_id: int,
    store_discord_name: str,
    store_name: str,
    store_owner_id: int,
    store_owner_name: str,
    store_address: str,
    used_for_data: bool,
    store_region_id: int,
    store_is_paid: bool,
    hub_discord_id: int,
    hub_discord_name: str,
    hub_name: str,
    hub_owner_id: int,
    hub_owner_name: str,
    hub_game_lock: int,
    hub_format_lock: int,
    hub_is_paid: bool,
    hub_region_id: int,
    hub_invite: str,
    game_id: int,
    game_name: str,
    format_id: int,
    format_name: str,
    last_ban_update: date,
    is_limited: bool,
    region_id: int,
    region_name: str,
) -> InteractionRow:
    store = (
        Store(
            store_discord_id,
            store_discord_name,
            store_name,
            store_owner_id,
            store_owner_name,
            store_address,
            used_for_data,
            store_region_id,
            store_is_paid,
        )
        if store_discord_id
        else None
    )
    hub = (
        Hub(
            hub_discord_id,
            hub_discord_name,
            hub_name,
            hub_owner_id,
            hub_owner_name,
            hub_region_id,
            hub_game_lock,
            hub_format_lock,
            hub_is_paid,
            hub_invite,
        )
        if hub_discord_id
        else None
    )
    game = Game(game_id, game_name) if game_id else None
    format = (
        Format(format_id, format_name, last_ban_update, is_limited)
        if format_id
        else None
    )
    region = Region(region_id, region_name) if region_id else None
    return InteractionRow(store, hub, game, format, region)


async def GetObjectsFromInteraction(interaction: Interaction) -> InteractionRow:
    discord_id = interaction.guild_id
    channel_id = interaction.channel_id
    if not interaction.channel or isinstance(
        interaction.channel, (DMChannel, GroupChannel)
    ):
        raise KnownError("No channel found")
    category_id = interaction.channel.category_id

    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=kwargs_row(interaction_row)) as cur,
    ):
        command = """
        WITH
            criteria AS (
                SELECT
                    %s AS discord_id,
                    %s AS category_id,
                    %s AS channel_id
            ),
            store_hub AS (
                SELECT
                    sv.discord_id AS store_discord_id,
                    sv.discord_name AS store_discord_name,
                    sv.store_name,
                    sv.owner_id AS store_owner_id,
                    sv.owner_name AS store_owner_name,
                    sv.store_address,
                    sv.used_for_data,
                    sv.region_id AS store_region_id,
                    sv.is_paid AS store_is_paid,
                    hv.discord_id AS hub_discord_id,
                    hv.discord_name AS hub_discord_name,
                    hv.hub_name,
                    hv.owner_id AS hub_owner_id,
                    hv.owner_name AS hub_owner_name,
                    hv.game_lock AS hub_game_lock,
                    hv.format_lock AS hub_format_lock,
                    hv.is_paid AS hub_is_paid,
                    hv.region_id AS hub_region_id,
                    hv.invite AS hub_invite,
                    COALESCE(gcm.game_id, COALESCE(hv.game_lock, gcmh.game_id)) AS game_id,
                    COALESCE(
                        fcm.format_id,
                        COALESCE(hv.format_lock, fcmh.format_id)
                    ) AS format_id,
                    COALESCE(
                        sv.region_id,
                        COALESCE(hv.region_id, rcm.region_id)
                    ) AS region_id
                FROM
                    discords d
                    INNER JOIN criteria c ON c.discord_id = d.discord_id
                    LEFT JOIN stores_view sv ON sv.discord_id = c.discord_id
                    LEFT JOIN game_category_maps gcm ON gcm.discord_id = sv.discord_id
                    AND gcm.category_id = c.category_id
                    LEFT JOIN format_channel_maps fcm ON fcm.discord_id = sv.discord_id
                    AND fcm.channel_id = c.channel_id
                    LEFT JOIN hubs_view hv ON hv.discord_id = d.discord_id
                    LEFT JOIN region_channel_maps rcm ON rcm.discord_id = hv.discord_id
                    AND rcm.channel_id = c.channel_id
                    LEFT JOIN game_category_maps gcmh ON gcmh.discord_id = hv.discord_id
                    AND gcmh.category_id = c.category_id
                    LEFT JOIN format_channel_maps fcmh ON fcmh.discord_id = hv.discord_id
                    AND fcmh.channel_id = c.channel_id
            )
        SELECT
            store_discord_id,
            store_discord_name,
            store_name,
            store_owner_id,
            store_owner_name,
            store_address,
            used_for_data,
            store_region_id,
            store_is_paid,
            hub_discord_id,
            hub_discord_name,
            hub_name,
            hub_owner_id,
            hub_owner_name,
            hub_game_lock,
            hub_format_lock,
            hub_is_paid,
            hub_region_id,
            hub_invite,
            g.id AS game_id,
            g.game_name,
            f.id AS format_id,
            f.format_name,
            f.last_ban_update,
            f.is_limited,
            r.id AS region_id,
            r.region_name
        FROM
            store_hub sh
            LEFT JOIN games g ON sh.game_id = g.id
            LEFT JOIN formats f ON sh.format_id = f.id
            LEFT JOIN regions r ON sh.region_id = r.id
        """

        await cur.execute(command, [discord_id, category_id, channel_id])
        row = await cur.fetchone()
        if not row:
            raise KnownError("No row found for the interaction")
        return row
