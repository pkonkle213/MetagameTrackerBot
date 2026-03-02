import psycopg
from psycopg.rows import TupleRow
from settings import DATABASE_URL
from tuple_conversions import Event, Format, Game, Store


def GetTournaments(store:Store, game:Game, format:Format) -> list[Event]:
  """Gets tournaments for the matching store, game, and format and returns them in reverse chronological order"""
  ...

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
      fs.event_id,
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

    cur.execute(command)
    standings = cur.fetchall()
    return standings

def GetEliminationPairings(event:Event) -> list[TupleRow]:
  """Gets the elimination rounds for events submitting with Pairings"""
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    WITH
      X AS (
        SELECT
          MAX(round_number) AS max_rounds,
          COUNT(DISTINCT player_name) AS players
        FROM
          full_pairings
        WHERE
          event_id = {event.id}
      )
    SELECT
      fp.round_number,
      INITCAP(COALESCE(ua1.archetype_played, 'Unknown')) AS p1_archetype_played,
      INITCAP(COALESCE(ua2.archetype_played, 'Unknown')) AS p2_archetype_played,
      fp.result
    FROM
      full_pairings fp
      LEFT JOIN unique_archetypes ua1 ON ua1.event_id = fp.event_id
      AND UPPER(ua1.player_name) = UPPER(fp.player_name)
      LEFT JOIN unique_archetypes ua2 ON ua2.event_id = fp.event_id
      AND UPPER(ua2.player_name) = UPPER(fp.player_name)
    WHERE
      fp.event_id = {event.id}
      AND result != 'LOSS'
      AND fp.round_number > (
        SELECT
          max_rounds
        FROM
          X
        LIMIT
          1
      ) - (
        SELECT
          CASE
            WHEN (
              SELECT
                players
              FROM
                X
              LIMIT
                1
            ) < 17 THEN 2
            ELSE 3
          END
      )
    ORDER BY
      fp.round_number DESC
    """

  cur.execute(command)
  rows = cur.fetchall()
  return rows