import psycopg
from psycopg.rows import TupleRow
from settings import DATABASE_URL
from tuple_conversions import Event

def GetEliminationStandings(event:Event) -> list[TupleRow]:
  """Gets the elimination rounds for events submitting with Standings"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    WITH
      FilteredStandings AS (
        SELECT
          *,
          COUNT(*) OVER () AS num_players
        FROM
          full_standings
        WHERE
          event_id = {event.id}
      )
    SELECT
      INITCAP(COALESCE(ua1.archetype_played, 'Unknown')) AS archetype_played,
      wins,
      losses,
      draws
    FROM
      FilteredStandings fs
      LEFT JOIN unique_archetypes ua1 ON ua1.event_id = fs.event_id
      AND UPPER(ua1.player_name) = UPPER(fs.player_name)
    ORDER BY
      (wins + losses + draws) DESC,
      wins DESC,
      draws DESC,
      losses DESC
    LIMIT
      CASE
        WHEN (
          SELECT
            num_players
          FROM
            FilteredStandings
          LIMIT
            1
        ) < 17 THEN 4
        ELSE 8
      END
    """

    cur.execute(command)  # type: ignore[arg-type]
    rows = cur.fetchall()
    
    return rows

def GetEliminationPairings(event:Event) -> list[TupleRow]:
  """Gets the elimination rounds for events submitting with Pairings"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      round_number,
      INITCAP(COALESCE(ua1.archetype_played, 'Unknown')) AS player1_archetype,
      player1_game_wins,
      INITCAP(COALESCE(ua2.archetype_played, 'Unknown')) AS player2_archetype,
      player2_game_wins
    FROM
      pairings p
      LEFT JOIN unique_archetypes ua1 ON ua1.event_id = p.event_id
      AND UPPER(ua1.player_name) = UPPER(p.player1_name)
      LEFT JOIN unique_archetypes ua2 ON ua2.event_id = p.event_id
      AND UPPER(ua2.player_name) = UPPER(p.player2_name)
    WHERE
      p.event_id = {event.id}
      AND round_number > CEIL(
        LOG(
          2,
          (
            SELECT
              COUNT(*)
            FROM
              full_standings
            WHERE
              event_id = {event.id}
          )
        )
      )
    ORDER BY
      round_number DESC
    """

    cur.execute(command)  # type: ignore[arg-type]
    rows = cur.fetchall()

    return rows