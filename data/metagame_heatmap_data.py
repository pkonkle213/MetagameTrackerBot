from datetime import date
from typing import NamedTuple

from psycopg import AsyncConnection
from psycopg.rows import class_row

from settings import DATABASE_URL


class MetagameHeatmapRow(NamedTuple):
    archetype: str
    player_count: int
    overall_win_percent: float | None
    opponent_archetype: str | None
    games_against: int | None
    matchup_win_percent: float | None


async def GetMetagameHeatmap(
    game_id: int,
    format_id: int,
    start_date: date,
    end_date: date,
    scope: str,
    scope_id: int | None = None,
) -> list[MetagameHeatmapRow]:
    scope_filters = {
        "data": ("s.used_for_data = TRUE", []),
        "store": ("s.discord_id = %s", [scope_id]),
        "hub": (
            """EXISTS (
                SELECT 1 FROM hubs_view hv
                WHERE hv.discord_id = %s
                    AND (
                        hv.region_id = s.region_id
                        OR EXISTS (
                            SELECT 1 FROM region_channel_maps rcm
                            WHERE rcm.discord_id = hv.discord_id
                                AND rcm.region_id = s.region_id
                        )
                    )
            )""",
            [scope_id],
        ),
    }
    if scope not in scope_filters:
        raise ValueError(f"Unsupported metagame heatmap scope: {scope}")

    scope_filter, scope_params = scope_filters[scope]
    command = f"""
        WITH eligible_events AS (
            SELECT e.id, e.discord_id
            FROM events e
            INNER JOIN stores_view s ON s.discord_id = e.discord_id
            WHERE e.game_id = %s
                AND e.format_id = %s
                AND e.event_date BETWEEN %s AND %s
                AND {scope_filter}
        ),
        archetype_counts AS (
            SELECT
                COALESCE(ua.archetype_played, 'Unknown') AS archetype,
                COUNT(*) AS player_count
            FROM full_standings fs
            INNER JOIN eligible_events ee ON ee.id = fs.event_id
            LEFT JOIN unique_archetypes ua
                ON ua.event_id = fs.event_id
                AND UPPER(ua.player_name) = UPPER(fs.player_name)
            GROUP BY COALESCE(ua.archetype_played, 'Unknown')
        ),
        pairing_records AS (
            SELECT
                COALESCE(player_arch.archetype_played, 'Unknown') AS archetype,
                COALESCE(opponent_arch.archetype_played, 'Unknown') AS opponent_archetype,
                UPPER(fp.result) AS result
            FROM full_pairings fp
            INNER JOIN eligible_events ee ON ee.id = fp.event_id
            LEFT JOIN unique_archetypes player_arch
                ON player_arch.event_id = fp.event_id
                AND UPPER(player_arch.player_name) = UPPER(fp.player_name)
            LEFT JOIN unique_archetypes opponent_arch
                ON opponent_arch.event_id = fp.event_id
                AND UPPER(opponent_arch.player_name) = UPPER(fp.opponent_name)
            WHERE UPPER(fp.opponent_name) <> 'BYE'
        ),
        overall_records AS (
            SELECT
                COALESCE(ua.archetype_played, 'Unknown') AS archetype,
                ROUND(
                    100.0 * SUM(fs.wins)
                    / NULLIF(SUM(fs.wins + fs.losses + fs.draws), 0),
                    1
                ) AS overall_win_percent
            FROM full_standings fs
            INNER JOIN eligible_events ee ON ee.id = fs.event_id
            LEFT JOIN unique_archetypes ua
                ON ua.event_id = fs.event_id
                AND UPPER(ua.player_name) = UPPER(fs.player_name)
            GROUP BY COALESCE(ua.archetype_played, 'Unknown')
        ),
        matchup_records AS (
            SELECT
                archetype,
                opponent_archetype,
                COUNT(*) AS games_against,
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE result = 'WIN')
                    / NULLIF(COUNT(*), 0),
                    1
                ) AS matchup_win_percent
            FROM pairing_records
            GROUP BY archetype, opponent_archetype
        )
        SELECT
            ac.archetype,
            ac.player_count,
            orc.overall_win_percent,
            mr.opponent_archetype,
            mr.games_against,
            mr.matchup_win_percent
        FROM archetype_counts ac
        LEFT JOIN overall_records orc ON orc.archetype = ac.archetype
        LEFT JOIN matchup_records mr ON mr.archetype = ac.archetype
        ORDER BY ac.player_count DESC, ac.archetype, mr.opponent_archetype
    """

    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(MetagameHeatmapRow)) as cur,
    ):
        await cur.execute(
            command,
            [game_id, format_id, start_date, end_date, *scope_params],
        )
        return await cur.fetchall()
