from psycopg.rows import class_row
import settings
import psycopg
from datetime import date
from settings import DATABASE_URL
from tuple_conversions import Event, Format, Game, Store, League, MetagameResult


def GetHubLeagueMetagame(league: League) -> list[MetagameResult]:
    metagame = """
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
        hls.league_id = 28
    GROUP BY
        archetype_played
    """
    data = GetLeagueMetagame(metagame)
    return data

def GetStoreLeagueMetagame(league: League) -> list[MetagameResult]:
    metagame = """
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
    data = GetLeagueMetagame(metagame)
    return data


def GetLeagueMetagame(metagame: str) -> list[MetagameResult]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(MetagameResult)) as cur:
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

        cur.execute(command)
        rows = cur.fetchall()
        return rows


def OneEventMetagame(event: Event) -> list[MetagameResult]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(MetagameResult)) as cur:
        command = f"""
        SELECT
            archetype_played,
            ROUND(metagame_percent * 100, 2) AS metagame_percent,
            ROUND(win_percent * 100, 2) AS win_percent
        FROM (
            SELECT
                COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
                1.0 * sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent,
                COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
            FROM
                full_standings fp
                LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id AND UPPER(fp.player_name) = UPPER(ua.player_name)
                INNER JOIN events e ON fp.event_id = e.id
                INNER JOIN stores s ON e.discord_id = s.discord_id
            WHERE
                e.id = {event.id}
            GROUP BY
                INITCAP(ua.archetype_played)
            )
        WHERE
        metagame_percent >= 0.02
        ORDER BY
        2 DESC,
        3 DESC
        """

        cur.execute(command)
        rows = cur.fetchall()
        return rows


def GetTheMetagame(criteria: str) -> list[MetagameResult]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(MetagameResult)) as cur:
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

        cur.execute(command)
        rows = cur.fetchall()
        return rows
