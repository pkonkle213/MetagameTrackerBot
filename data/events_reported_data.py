import os
import psycopg2

def GetStoreReportedPercentage(discord_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.event_date,
      s.store_name,
      f.name,
      ROUND(100.0 * COUNT(*) FILTER (WHERE archetype_played IS NOT NULL) / COUNT(*), 2) as reported_percent
    FROM (
      SELECT e.id, asu.archetype_played
      FROM Events e
      INNER JOIN participants p on p.event_id = e.id
      LEFT JOIN (SELECT DISTINCT on (event_id, player_name)
                   event_id, player_name, archetype_played, submitter_id
                 FROM ArchetypeSubmissions
                 ORDER BY event_id, player_name, id desc) asu ON asu.event_id = e.id and asu.player_name = p.player_name
      {f'WHERE e.discord_id = {discord_id}' if discord_id != 0 else ''}
      ORDER BY e.id desc
    ) x
    INNER JOIN events e ON x.id = e.id
    INNER JOIN formats f ON f.id = e.format_id
    INNER JOIN stores s ON s.discord_id = e.discord_id
    WHERE s.used_for_data = {True}
    GROUP BY e.event_date, s.store_name, f.name
    ORDER BY e.event_date desc, s.store_name, f.name
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows