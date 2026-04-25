import psycopg
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store

def GetUserArchetypes(
  userId: int,
  game:Game,
  format:Format
) -> list[str]:
  """Get's a suggested list of archetypes for the user"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = """
    SELECT
      INITCAP(ua.archetype_played) AS archetype_played
    FROM
      unique_archetypes ua
      INNER JOIN events e ON e.id = ua.event_id
      INNER JOIN player_names pn ON e.discord_id = pn.discord_id
      AND upper(ua.player_name) = upper(pn.player_name)
    WHERE
      pn.submitter_id = %s
      AND e.game_id = %s
      AND e.format_id = %s
    GROUP BY
      INITCAP(ua.archetype_played)
    ORDER BY
      COUNT(*) DESC
    LIMIT
      10
    """

    criteria = [userId, game.id, format.id]
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return [row[0] for row in rows]

def GetUserName(
  userId: int
) -> str:
  """Gets the user's name from the database"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = """
    SELECT
      player_name
    FROM
      player_names
    WHERE
      submitter_id = %s
    GROUP BY
      player_name
    ORDER BY
      COUNT(*) DESC
    """

    criteria = [userId]
    cur.execute(command, criteria)
    row = cur.fetchone()
    return row[0] if row else ''
