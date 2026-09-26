from datetime import date

from psycopg import AsyncConnection
from psycopg.rows import TupleRow

from settings import DATABASE_URL
from tuple_conversions import Format, Game


async def GetPersonalMatchups(
    discord_id: int,
    game: Game,
    format: Format,
    start_date: date,
    end_date: date,
    user_id: int,
) -> list[TupleRow]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        command = f"""
        SELECT
            COALESCE(INITCAP(ua.archetype_played), 'UNKNOWN') AS archetype_played,
            COUNT(*) as total_matches,
            COUNT(CASE WHEN result = 'WIN' THEN 1 END) as wins,
            COUNT(CASE WHEN result = 'LOSS' THEN 1 END) as losses,
            COUNT(CASE WHEN result = 'DRAW' THEN 1 END) as draws,
            ROUND(1.0 * COUNT(CASE WHEN result = 'WIN' THEN 1 END) / (COUNT(CASE WHEN result = 'WIN' THEN 1 END) + COUNT(CASE WHEN result = 'LOSS' THEN 1 END) + COUNT(CASE WHEN result = 'DRAW' THEN 1 END)) * 100, 2) as win_percent
        FROM
            full_pairings fp
            INNER JOIN events e ON fp.event_id = e.id
            LEFT JOIN unique_archetypes ua ON UPPER(fp.opponent_name) = UPPER(ua.player_name)
            AND ua.event_id = fp.event_id
            INNER JOIN player_names pn ON pn.discord_id = e.discord_id
            AND UPPER(fp.player_name) = UPPER(pn.player_name)
        WHERE
            pn.submitter_id = {user_id}
            AND UPPER(fp.opponent_name) != 'BYE'
            AND e.discord_id = {discord_id}
            AND e.game_id = {game.id}
            AND e.format_id = {format.id}
            AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY
            INITCAP(ua.archetype_played)
        ORDER BY
            2 DESC,
            1
        """

        await cur.execute(command)  # type: ignore[arg-type]
        rows = await cur.fetchall()
        return rows
