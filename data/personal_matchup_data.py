from datetime import date
from settings import DATABASE_URL
import psycopg

from tuple_conversions import Format, Game

def GetPersonalMatchups(
  discord_id:int,
  game:Game,
  format:Format,
  start_date:date,
  end_date:date,
  user_id:int
):
  conn = psycopg.connect(DATABASE_URL)
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
      LEFT JOIN unique_archetypes ua ON UPPER(fp.opponent_name) = UPPER(ua.player_name)
        AND ua.event_id = fp.event_id
      INNER JOIN player_names pn ON pn.discord_id = e.discord_id
        AND UPPER(fp.player_name) = UPPER(pn.player_name)
    WHERE
      pn.submitter_id = {user_id}
      AND UPPER(fp.opponent_name) != 'BYE'
      AND e.discord_id = {discord_id}
      AND e.game_id = {game.GameId}
      AND e.format_id = {format.FormatId}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY UPPER(ua.archetype_played)
    ORDER BY COUNT(*) DESC, 
      UPPER(ua.archetype_played)
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows