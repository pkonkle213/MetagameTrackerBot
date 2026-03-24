import psycopg
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store

def GetUserArchetypes(
  store: Store,
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
      AND pn.discord_id = %s
      AND e.game_id = %s
      AND e.format_id = %s
    GROUP BY
      INITCAP(ua.archetype_played)
    ORDER BY
      COUNT(*) DESC
    LIMIT
      10
    """

    criteria = [userId, store.discord_id, game.id, format.formaid
    cur.execute(command, criteria)
    rows = cur.fetchall()
    return [row[0] for row in rows]

#TODO: I think this is duplicate code....GetPlayerName
def GetUserName(
  store: Store,
  userId: int
) -> str | None:
  """Gets the user's name from the database"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = """
    SELECT
      player_name
    FROM
      player_names
    WHERE
      discord_id = %s
      AND submitter_id = %s
    """

    criteria = [store.discord_id, userId]
    cur.execute(command, criteria)
    row = cur.fetchone()
    return row[0] if row else None
