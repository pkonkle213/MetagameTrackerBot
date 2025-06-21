import os
import psycopg2

def GetAttendance(store,
                  game,
                  format,
                  start_date,
                  end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT e.event_date,
      {'s.store_name,' if not store else ''}
      {'f.name,' if not format else ''}
      COUNT(*)
    FROM Events e
      INNER JOIN Participants p on e.id = p.event_id
      INNER JOIN Stores s on s.discord_id = e.discord_id
      INNER JOIN Formats f on f.id = e.format_id
    WHERE e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game.ID} 
      AND s.used_for_data = {True}
      {f'AND e.discord_id = {store.DiscordId}' if store else ''}
      {f'AND e.format_id = {format.ID}' if format else ''}
    GROUP BY e.id
      {', f.name' if not format else ''}
      {', s.store_name' if not store else ''}
    ORDER BY e.event_date DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows