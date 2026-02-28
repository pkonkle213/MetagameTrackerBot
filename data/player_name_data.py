import psycopg
from settings import DATABASE_URL
from tuple_conversions import Format, Game, Store

#TODO: I would love to give the top 5 previous archetypes of the player as well as the top 10 in general, but I need to find a awy to UNION the two lists without removing the sorting
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
    WITH
      X AS (
        SELECT
          ua.event_id,
          ua.player_name,
          pn.submitter_id,
          ua.archetype_played
        FROM
          unique_archetypes ua
          INNER JOIN player_names pn ON INITCAP(ua.player_name) = INITCAP(pn.player_name)
          INNER JOIN events e ON e.id = ua.event_id
        WHERE
          e.discord_id = %s
          AND e.game_id = %s
          AND e.format_id = %s
      )
    SELECT
      INITCAP(archetype_played) AS archetype_played
    FROM
      X
    WHERE
      X.submitter_id = %s
    GROUP BY
      INITCAP(archetype_played)
    ORDER BY
      1.0 * COUNT(*) / SUM(COUNT(*)) OVER () DESC
    LIMIT
      5
    """

    criteria = [store.DiscordId, game.GameId, format.FormatId, userId]
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

    criteria = [store.DiscordId, userId]
    cur.execute(command, criteria)
    row = cur.fetchone()
    return row[0] if row else None
