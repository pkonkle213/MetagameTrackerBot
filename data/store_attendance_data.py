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
      e.event_date,
      {'s.store_name,' if store.DiscordId == DATAGUILDID else ''}
      {'f.name,' if not format else ''}
      COUNT(*)
    FROM
      full_standings fp
      INNER JOIN events e ON e.id = fp.event_id
      INNER JOIN Stores s ON s.discord_id = e.discord_id
      INNER JOIN Formats f ON f.id = e.format_id
    WHERE
      e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.game_id = {game.ID}
      AND e.format_id = {format.ID}
      AND s.used_for_data = TRUE
      {f'AND e.discord_id = {store.DiscordId}' if store.DiscordId != DATAGUILDID else ''}
    GROUP BY
      {'e.format_id,' if not format else ''}
      {'s.store_name,' if store.DiscordId == DATAGUILDID else ''}
      e.event_date,
      e.game_id
    ORDER BY
      e.event_date DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows