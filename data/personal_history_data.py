from datetime import date

from psycopg import AsyncConnection
from psycopg.rows import TupleRow

from settings import DATABASE_URL, DATAGUILDID
from tuple_conversions import Format, Game, Hub, Region, Store


async def GetStorePairingsHistory(
    user_id: int,
    store: Store,
    game: Game | None,
    format: Format | None,
    start_date: date,
    end_date: date,
) -> list[TupleRow]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
            TO_CHAR(e.event_date, 'MM/DD') as event_date,
            {"INITCAP(g.game_name) AS game_name," if not game else ""}
            {"INITCAP(f.format_name) AS format_name," if not format else ""}
            fp.round_number,
            COALESCE(uap.archetype_played, 'Unknown') as players_archetype,
            CASE
                WHEN UPPER(fp.opponent_name) = 'BYE' THEN 'Bye'
                ELSE COALESCE(uao.archetype_played, 'Unknown')
            END AS opponents_archetype,
            INITCAP(fp.result) as result
        FROM
            full_pairings fp
            INNER JOIN events e ON e.id = fp.event_id
            INNER JOIN stores_view s ON s.discord_id = e.discord_id
            INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fp.player_name) AND pn.discord_id = s.discord_id
            LEFT JOIN unique_archetypes uap ON uap.event_id = e.id AND UPPER(uap.player_name) = UPPER(pn.player_name)
            LEFT JOIN unique_archetypes uao ON uao.event_id = e.id AND UPPER(uao.player_name) = UPPER(fp.opponent_name)
            INNER JOIN games g ON g.id = e.game_id
            INNER JOIN formats f ON f.id = e.format_id
        WHERE
            pn.submitter_id = {user_id}
            AND s.discord_id = {store.discord_id}
            AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
            {f"AND e.game_id = {game.id}" if game else ""}
            {f"AND e.format_id = {format.id}" if format else ""}
        ORDER BY
            e.event_date DESC,
            fp.round_number
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows


async def GetHubPairingsHistory(
    user_id: int,
    hub: Hub,
    region: Region | None,
    game: Game | None,
    format: Format | None,
    start_date: date,
    end_date: date,
) -> list[TupleRow]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
            TO_CHAR(e.event_date, 'MM/DD/YYYY') AS event_date,
            s.store_name,
            {"INITCAP(r.region_name) AS region_name," if not region else ""}
            {"INITCAP(g.game_name) AS game_name," if not game else ""}
            {"INITCAP(f.format_name) AS format_name," if not format else ""}
            fp.round_number,
            COALESCE(uap.archetype_played, 'Unknown') AS players_archetype,
            CASE
            WHEN UPPER(fp.opponent_name) = 'BYE' THEN 'Bye'
            ELSE COALESCE(uao.archetype_played, 'Unknown')
            END AS opponents_archetype,
            INITCAP(fp.result) AS result
        FROM
            full_pairings fp
            INNER JOIN events e ON e.id = fp.event_id
            INNER JOIN stores_view s ON s.discord_id = e.discord_id
            INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fp.player_name)
            AND pn.discord_id = s.discord_id
            LEFT JOIN unique_archetypes uap ON uap.event_id = e.id
            AND UPPER(uap.player_name) = UPPER(pn.player_name)
            LEFT JOIN unique_archetypes uao ON uao.event_id = e.id
            AND UPPER(uao.player_name) = UPPER(fp.opponent_name)
            INNER JOIN games g ON g.id = e.game_id
            INNER JOIN formats f ON f.id = e.format_id
            INNER JOIN regions r ON r.id = s.region_id
            INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = s.discord_id
            AND sah.game_id = e.game_id
            AND sah.format_id = e.format_id
            AND sah.region_id = s.region_id
        WHERE
            pn.submitter_id = {user_id}
            AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
            AND sah.hub_discord_id = {hub.discord_id}
            {f"AND e.game_id = {game.id}" if game else ""}
            {f"AND e.format_id = {format.id}" if format else ""}
            {f"AND s.region_id = {region.id}" if region else ""}
        ORDER BY
            e.event_date DESC,
            fp.round_number
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows


async def GetHubStandingsHistory(
    user_id: int,
    hub: Hub,
    region: Region | None,
    game: Game | None,
    format: Format | None,
    start_date: date,
    end_date: date,
) -> list[TupleRow]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
            TO_CHAR(ev.event_date, 'MM/DD/YYYY') AS event_date,
            {"r.region_name," if not region else ""}
            sv.store_name,
            {"INITCAP(g.game_name) AS game_name," if not game else ""}
            {"INITCAP(f.format_name) AS format_name," if not format else ""}
            COALESCE(ua.archetype_played, 'Unknown') as archetype_played,
            wins,
            losses,
            draws
        FROM
            full_standings fs
            INNER JOIN events_view ev ON ev.id = fs.event_id
            INNER JOIN player_names pn ON pn.discord_id = ev.discord_id
            AND upper(pn.player_name) = upper(fs.player_name)
            INNER JOIN games g ON g.id = ev.game_id
            INNER JOIN formats f ON f.id = ev.format_id
            INNER JOIN stores_view sv ON sv.discord_id = ev.discord_id
            INNER JOIN regions r ON r.id = sv.region_id
            INNER JOIN stores_approved_hubs sah ON sah.store_discord_id = sv.discord_id
            AND sah.format_id = ev.format_id
            AND sah.game_id = ev.game_id
            AND sah.region_id = sv.region_id
            LEFT JOIN unique_archetypes ua ON ua.event_id = ev.id
            AND upper(ua.player_name) = upper(fs.player_name)
        WHERE
            pn.submitter_id = {user_id}
            AND sah.hub_discord_id = {hub.discord_id}
            AND ev.event_date BETWEEN '{start_date}' AND '{end_date}'
            {f"AND ev.game_id = {game.id}" if game else ""}
            {f"AND ev.format_id = {format.id}" if format else ""}
            {f"AND sv.region_id = {region.id}" if region else ""}
        ORDER BY
            ev.event_date DESC
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows


async def GetStoreStandingsHistory(
    user_id: int,
    store: Store,
    game: Game | None,
    format: Format | None,
    start_date: date,
    end_date: date,
) -> list[TupleRow]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
            TO_CHAR(event_date, 'MM/DD/YYYY') as event_date,
            {"INITCAP(g.game_name) AS game_name," if not game else ""}
            {"INITCAP(f.format_name) AS format_name," if not format else ""}
            COALESCE(archetype_played, 'Unknown') as archetype_played,
            wins,
            losses,
            draws
        FROM
            full_standings fp
            INNER JOIN events e ON e.id = fp.event_id
            INNER JOIN stores_view s ON s.discord_id = e.discord_id
            INNER JOIN games g ON g.id = e.game_id
            INNER JOIN formats f ON f.id = e.format_id
            INNER JOIN player_names pn ON pn.discord_id = e.discord_id AND UPPER(pn.player_name) = UPPER(fp.player_name)
            LEFT JOIN unique_archetypes uar ON uar.event_id = e.id AND UPPER(uar.player_name) = UPPER(pn.player_name)
        WHERE
            pn.submitter_id = {user_id}
            AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
            AND s.discord_id = {store.discord_id}
            {f"AND e.game_id = {game.id}" if game else ""}
            {f"AND e.format_id = {format.id}" if format else ""}
        ORDER BY
            e.event_date DESC
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows
