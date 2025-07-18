from settings import DATAGUILDID
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
    SELECT
      fr.event_date,
      {'s.store_name,' if store.DiscordId == DATAGUILDID else ''}
      {'f.name,' if not format else ''}
      COUNT(*)
    FROM
      fullresults fr
      INNER JOIN Stores s ON s.discord_id = fr.discord_id
      INNER JOIN Formats f ON f.id = fr.format_id
    WHERE
      fr.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.used_for_data = {True}
      AND fr.game_id = {game.ID} 
      AND fr.format_id = 1
      {f'AND f.discord_id = {store.DiscordId}' if store.DiscordId != DATAGUILDID else ''}
    GROUP BY
      {'fr.format_id,' if not format else ''}
      {'s.store_name,' if store.DiscordId == DATAGUILDID else ''}
      fr.event_date,
      fr.game_id
    ORDER BY
      fr.event_date DESC
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows