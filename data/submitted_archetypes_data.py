from datetime import date

from psycopg import AsyncConnection
from settings import DATABASE_URL

from tuple_conversions import Format, Game, Store


async def GetSubmittedArchetypes(
    game: Game,
    format: Format | None,
    store: Store,
    player_name: str | None,
    date_used: date | None,
):
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        selected_format = "" if format is not None else "f.format_name,"
        filters = [
            "ua.reported = FALSE",
            "e.discord_id = %s",
            "e.game_id = %s",
        ]
        criteria: list[object] = [store.discord_id, game.id]

        if format is not None:
            filters.append("e.format_id = %s")
            criteria.append(format.id)
        if date_used is not None:
            filters.append("e.event_date = %s")
            criteria.append(date_used)
        if player_name:
            filters.append("UPPER(ua.player_name) = UPPER(%s)")
            criteria.append(player_name)

        command = f"""
        SELECT e.event_date,
            {selected_format}
            INITCAP(ua.player_name) as player_name,
            ua.archetype_played,
            ua.submitter_username,
            ua.asu_submitter_id
        FROM unique_archetypes ua
            INNER JOIN events e ON ua.event_id = e.id
            INNER JOIN formats f ON f.id = e.format_id
        WHERE {" AND ".join(filters)}
        ORDER BY
            e.event_date DESC,
            ua.player_name
        LIMIT 15
        """

        await cur.execute(command, criteria)
        rows = await cur.fetchall()
        return rows