import os
import psycopg2

def GetStoreReportedPercentage(discord_id,
                              game,
                              format):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.event_date,
      {'f.name,' if not format else ''}
      ROUND(100.0 * COUNT(*) FILTER (WHERE archetype_played IS NOT NULL) / COUNT(*), 2) as reported_percent
    FROM (
      SELECT e.id, asu.archetype_played
      FROM Events e
      INNER JOIN participants p on p.event_id = e.id
      LEFT JOIN (SELECT DISTINCT on (event_id, player_name)
                   event_id, player_name, archetype_played, submitter_id
                 FROM ArchetypeSubmissions
                 ORDER BY event_id, player_name, id desc) asu ON asu.event_id = e.id and asu.player_name = p.player_name
      WHERE e.discord_id = {discord_id}
        AND game_id = {game.ID}
        {f'AND format_id = {format.ID}' if format else ''}
      ORDER BY e.id desc
    ) x
    INNER JOIN events e ON x.id = e.id
    INNER JOIN formats f ON f.id = e.format_id
    GROUP BY e.event_date{', f.name' if not format else ''}
    ORDER BY e.event_date desc{', name' if not format else ''}
    '''
    cur.execute(command)
    rows = cur.fetchall()
    return rows