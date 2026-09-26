from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row, scalar_row

from custom_errors import KnownError
from settings import DATABASE_URL
from tuple_conversions import Event, Format, Game, Hub, PlayerArchetype, Region, Store


async def CompleteEvent(event_id: int) -> bool:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
        UPDATE
            events
        SET
            is_complete = TRUE
        WHERE
            id = %s
        RETURNING
            id
        """

        await cur.execute(command, [event_id])
        await conn.commit()
        row = await cur.fetchone()
        return bool(row)


async def GetEvent(event_id: int) -> Event:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Event)) as cur,
    ):
        command = """
        SELECT
            id,
            custom_event_id,
            discord_id,
            event_date,
            game_id,
            format_id,
            last_update,
            event_type_id,
            event_name,
            reported_as,
            league_id,
            created_by,
            created_at,
            is_complete
        FROM
            events_view
        WHERE
            id = %s
        """

        await cur.execute(command, [event_id])
        row = await cur.fetchone()
        if not row:
            raise KnownError(f"Cannot find event. ID: {event_id}")
        return row


async def CreateEvent(event: Event, user_id: int) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = f"""
        INSERT INTO Events
        (event_date
        , discord_id
        , game_id
        , format_id
        , last_update
        , event_name
        , event_type_id
        , created_at
        , created_by
        , league_id
        , custom_event_id
        )
        VALUES
        ('{event.event_date}'
        , {event.discord_id}
        , {event.game_id}
        , {event.format_id}
        , 0
        , '{event.event_name}'
        , {event.event_type_id if int(event.event_type_id) > 0 else 3}
        , CURRENT_TIMESTAMP AT TIME ZONE 'America/New_York'
        , {user_id}
        , {-int(event.event_type_id) if int(event.event_type_id) < 0 else "NULL"}
        , {event.custom_event_id if event.custom_event_id else "NULL"}
        )
        RETURNING id
        """

        await cur.execute(command)  # type: ignore[arg-type]
        event_id = await cur.fetchone()

        if not event_id:
            raise KnownError("Unable to create event")
        return event_id


async def GetPlayersInEvent(event_id: int) -> list[PlayerArchetype]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(PlayerArchetype)) as cur,
    ):
        command = """
        SELECT
            INITCAP(fs.player_name) as player_name,
            INITCAP(ua.archetype_played) as archetype_played
        FROM
            full_standings fs
            LEFT JOIN unique_archetypes ua ON ua.event_id = fs.event_id
            AND upper(ua.player_name) = upper(fs.player_name)
        WHERE
            fs.event_id = %s
        ORDER BY
            INITCAP(fs.player_name)
        """

        await cur.execute(command, [event_id])
        rows = await cur.fetchall()

        return rows


class EventResult(NamedTuple):
    archetype_played: str
    wins: int
    losses: int
    draws: int


async def GetEventDetails(event_id: int) -> list[EventResult]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(EventResult)) as cur,
    ):
        command = """
        SELECT
            COALESCE(REGEXP_REPLACE(INITCAP(archetype_played), '''S', '''s', 'g'), 'Unknown') AS archetype_played,
            wins,
            losses,
            draws
        FROM
            full_standings fp
            LEFT JOIN unique_archetypes ua ON ua.event_id = fp.event_id
            AND UPPER(ua.player_name) = UPPER(fp.player_name)
        WHERE
            fp.event_id = %s
        ORDER BY
            2 DESC,
            4 DESC,
            3 DESC,
            1
        """

        await cur.execute(command, [event_id])  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows


async def DeleteStandingsFromEvent(event_id: int) -> None:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = """
        DELETE FROM standings
        WHERE event_id = %s
        """

        await cur.execute(command, [event_id])
        await conn.commit()


# TODO: Needs Region Locked Hubs
async def GetEvents(
    store: Store | None,
    hub: Hub | None,
    game: Game,
    format: Format,
    region: Region | None,
    is_submitter: bool,
) -> list[Event]:
    time_range = 4 if is_submitter else 2
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(Event)) as cur,
    ):
        command = f"""
        WITH
          criteria AS (
            SELECT
              {store.discord_id if store else "NULL::BIGINT"} AS store_discord_id,
              {hub.discord_id if hub else "NULL::BIGINT"} as hub_discord_id,
              {game.id} AS game_id,
              {format.id} AS format_id,
              {region.id if region else "NULL::INT"} AS region_id
          )
        (
          --Store Events
          SELECT
            e.id,
            e.custom_event_id,
            e.discord_id,
            e.event_date,
            e.game_id,
            e.format_id,
            e.last_update,
            e.event_name,
            e.event_type_id,
            e.reported_as,
            e.created_by,
            e.created_at,
            e.league_id,
            e.is_complete
          FROM
            events_view e
            INNER JOIN criteria c ON c.store_discord_id = e.discord_id
            AND c.game_id = e.game_id
            AND c.format_id = e.format_id
          WHERE
            e.event_date >= CURRENT_DATE - INTERVAL '{time_range} weeks'
        )
        UNION ALL
        (
          --Format Locked Hubs
          SELECT
            e.id,
            e.custom_event_id,
            e.discord_id,
            e.event_date,
            e.game_id,
            e.format_id,
            e.last_update,
            s.store_name || ' - ' || e.event_name AS event_name,
            e.event_type_id,
            e.reported_as,
            e.created_by,
            e.created_at,
            e.league_id,
            e.is_complete
          FROM
            events_view e
            INNER JOIN stores s ON s.discord_id = e.discord_id
            INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = e.discord_id
            AND sah.game_id = e.game_id
            AND sah.format_id = e.format_id
            INNER JOIN hubs_view h ON h.discord_id = sah.hub_discord_id
            INNER JOIN region_channel_maps rcm ON rcm.discord_id = h.discord_id
            AND rcm.region_id = s.region_id
            INNER JOIN criteria c ON c.hub_discord_id = h.discord_id
            AND c.game_id = h.game_lock
            AND c.format_id = h.format_lock
            AND c.region_id = rcm.region_id
          WHERE
            e.event_date >= CURRENT_DATE - INTERVAL '{time_range} weeks'
        )
        ORDER BY
          event_date DESC
        LIMIT
          25
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows
