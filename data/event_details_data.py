from tuple_conversions import Format, Game, Store
from settings import DATABASE_URL
import psycopg


def GetAllEventsStats(store: Store, game: Game, format: Format):
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor() as cur:
        command = f"""
        SELECT
          e.event_date,
          er.reported,
          p.players,
          round(100.0 * reported_percent, 2) AS percent_reported,
          a.submitters,
          round(100.0 * a.submitters / p.players, 2) AS percent_unique
        FROM
          (
            SELECT
              event_id,
              count(*) AS players
            FROM
              full_standings
            GROUP BY
              event_id
          ) p
          INNER JOIN events_reported er ON er.id = p.event_id
          INNER JOIN (
            SELECT
              event_id,
              count(DISTINCT submitter_id) AS submitters
            FROM
              archetype_submissions
            GROUP BY
              event_id
          ) a ON p.event_id = a.event_id
          INNER JOIN events e ON e.id = p.event_id
          INNER JOIN games g ON g.id = e.game_id
          INNER JOIN formats f ON f.id = e.format_id
          INNER JOIN stores s ON s.discord_id = e.discord_id
        WHERE
          e.discord_id = {store.discord_id}
          AND g.id = {game.id}
          AND f.id = {format.id}
        ORDER BY
          p.event_id DESC
        """

        cur.execute(command)
        rows = cur.fetchall()
        return rows
