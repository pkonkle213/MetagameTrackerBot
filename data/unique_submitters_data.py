from settings import DATABASE_URL
import psycopg2

def GetUniqueSubmittersPercentage(discord_id:int):
  conn = psycopg2.connect(DATABASE_URL)
  with conn, conn.cursor() as cur:
    command = f"""
    SELECT
      e.event_date,
      {'s.store_name,' if not discord_id else ''}
      g.name AS game,
      f.name AS format,
      a.submitters,
      p.players,
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
      INNER JOIN (
        SELECT
          event_id,
          count(DISTINCT submitter_id) AS submitters
        FROM
          archetypesubmissions
        GROUP BY
          event_id
      ) a ON p.event_id = a.event_id
      INNER JOIN events e ON e.id = p.event_id
      INNER JOIN games g ON g.id = e.game_id
      INNER JOIN formats f ON f.id = e.format_id
      INNER JOIN stores s ON s.discord_id = e.discord_id
    {f'WHERE e.discord_id = {discord_id}' if discord_id else ''}
    ORDER BY
      p.event_id DESC
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows
