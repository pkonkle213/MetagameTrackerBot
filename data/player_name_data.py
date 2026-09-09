import psycopg
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store


def GetUserArchetypes(
    user_id: int,
    category_id: int,
    channel_id: int) -> list[str]:
    """Get's a suggested list of archetypes for the user"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor() as cur:
        command = f"""
        SELECT
            INITCAP(ua.archetype_played) AS archetype_played
        FROM
            unique_archetypes ua
            INNER JOIN events e ON e.id = ua.event_id  
            INNER JOIN game_category_maps gcm ON gcm.game_id = e.game_id  
            INNER JOIN format_channel_maps fcm ON fcm.format_id = e.format_id
            INNER JOIN player_names pn ON e.discord_id = pn.discord_id
            AND upper(ua.player_name) = upper(pn.player_name)
        WHERE
            pn.submitter_id = {user_id}
            AND gcm.category_id = {category_id}
            AND fcm.channel_id = {channel_id}
        GROUP BY
            INITCAP(ua.archetype_played)
        ORDER BY
            COUNT(*) DESC
        LIMIT
            10
        """

        cur.execute(command)
        rows = cur.fetchall()
        return [row[0] for row in rows]


def GetUserName(discord_id: int, user_id: int) -> str:
    """Gets the user's name from the database"""
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor() as cur:
        command = f"""
        SELECT
            player_name
        FROM
            player_names pn
            LEFT JOIN stores_approved_hubs sah ON sah.store_discord_id = pn.discord_id
        WHERE
            submitter_id = {user_id}
            AND (
                pn.discord_id = {discord_id}
                OR sah.hub_discord_id = {discord_id}
            )
        GROUP BY
            player_name
        ORDER BY
            COUNT(*) DESC
        LIMIT 1
        """

        cur.execute(command)
        row = cur.fetchone()
        return row[0] if row else ""
