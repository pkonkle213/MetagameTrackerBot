import os
import psycopg2

def GetPersonalMatchups(discord_id, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      COALESCE(UPPER(ua.archetype_played), 'UNKNOWN') AS archetype_played,
      COUNT(CASE WHEN result = 'WIN' THEN 1 END) as wins,
      COUNT(CASE WHEN result = 'LOSS' THEN 1 END) as losses,
      COUNT(CASE WHEN result = 'DRAW' THEN 1 END) as draws,
      COUNT(*) as total_matches,
      ROUND(1.0 * COUNT(CASE WHEN result = 'WIN' THEN 1 END) / (COUNT(CASE WHEN result = 'WIN' THEN 1 END) + COUNT(CASE WHEN result = 'LOSS' THEN 1 END) + COUNT(CASE WHEN result = 'DRAW' THEN 1 END)) * 100, 2) as win_percent
    FROM
      full_pairings fp
      INNER JOIN events e ON fp.event_id = e.id
      LEFT JOIN unique_archetypes ua ON fp.opponent_name = ua.player_name
      AND ua.event_id = fp.event_id
    WHERE
      UPPER(fp.player_name) IN (
        SELECT player_name
        FROM player_names
        WHERE discord_id = {discord_id}
        AND submitter_id = {user_id})
      AND UPPER(fp.opponent_name) != 'BYE'
      AND e.discord_id = {discord_id}
      AND e.game_id = {game.ID}
      AND e.format_id = {format.ID}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY UPPER(ua.archetype_played)
    ORDER BY COUNT(*) DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows