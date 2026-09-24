from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL
from tuple_conversions import Event, League, MetagameResult


# TODO: Something feels like I could consolidate these into fewer functions
async def GetHubLeagueMetagame(league: League) -> list[MetagameResult]:
    metagame = f"""
    SELECT
        INITCAP(COALESCE(ua.archetype_played, 'Unknown')) AS archetype_played,
        sum(fs.wins) / (sum(fs.wins) + sum(fs.losses) + sum(fs.draws)) AS win_percent,
        COUNT(*) / SUM(count(*)) OVER () AS metagame_percent
    FROM
        full_standings fs
        INNER JOIN events_view e ON e.id = fs.event_id
        INNER JOIN hub_league_stores hls ON e.discord_id = hls.store_discord_id
        LEFT JOIN unique_archetypes ua ON fs.event_id = ua.event_id AND UPPER(fs.player_name) = upper(ua.player_name)
    WHERE
        hls.league_id = {league.id}
    GROUP BY
        archetype_played
    """
    data = await GetLeagueMetagame(metagame)
    return data


async def GetStoreLeagueMetagame(league: League) -> list[MetagameResult]:
    metagame = f"""
    SELECT
        COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
        sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent,
        COUNT(*) / SUM(count(*)) OVER () AS metagame_Percent
    FROM
        full_standings fp
        LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id
        AND UPPER(fp.player_name) = UPPER(ua.player_name)
        INNER JOIN events e ON fp.event_id = e.id
    WHERE
        e.league_id = {league.id}
    GROUP BY
        INITCAP(ua.archetype_played)
    """
    data = await GetLeagueMetagame(metagame)
    return data


async def GetLeagueMetagame(metagame: str) -> list[MetagameResult]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(MetagameResult)) as cur,
    ):
        command = f"""
        WITH
            metagame AS (
                {metagame}
            )
        SELECT
            archetype_played,
            ROUND(metagame_percent * 100, 2) AS metagame_percent,
            ROUND(win_percent * 100, 2) AS win_percent
        FROM
            metagame
        WHERE
            metagame_percent >= 0.02
        ORDER BY
            2 DESC,
            3 DESC
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows


async def OneEventMetagame(event: Event) -> list[MetagameResult]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(MetagameResult)) as cur,
    ):
        command = """
        WITH metagame AS (
            SELECT
                COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
                COUNT(*) * 1.0 / SUM(count(*)) OVER () AS metagame_Percent,
                1.0 * sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent
            FROM
                full_standings fp
                LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id AND UPPER(fp.player_name) = UPPER(ua.player_name)
                INNER JOIN events e ON fp.event_id = e.id
                INNER JOIN stores s ON e.discord_id = s.discord_id
            WHERE
                e.id = %s
            GROUP BY
                INITCAP(ua.archetype_played)
            )
        SELECT
            archetype_played,
            ROUND(metagame_percent * 100, 2) AS metagame_percent,
            ROUND(win_percent * 100, 2) AS win_percent
        FROM
            metagame
        WHERE
            metagame_percent >= 0.02
        ORDER BY
            2 DESC,
            3 DESC
        """

        await cur.execute(command, [event.id])
        rows = await cur.fetchall()
        return rows


async def GetTheMetagame(criteria: str) -> list[MetagameResult]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(MetagameResult)) as cur,
    ):
        command = f"""
        WITH
            RESULTS AS (
                {criteria}
            ),
            GROUPED AS (
                SELECT
                    archetype_played,
                    1.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percent,
                    COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
                FROM
                    RESULTS
                GROUP BY
                    archetype_played
            )
        SELECT
            archetype_played,
            ROUND(metagame_percent * 100, 2) AS metagame_percent,
            ROUND(win_percent * 100, 2) AS win_percent
        FROM
            GROUPED
        WHERE
            metagame_percent >= 0.02
        ORDER BY
            2 DESC,
            3 DESC
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows
