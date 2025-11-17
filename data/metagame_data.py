import settings
import os
import psycopg2

from tuple_conversions import Store

#TODO: To implement this, it will require two new columns in the database, editing the Store object in tuple_conversions, and updating all queries that use or return the Store object.
"""
def GetAreaForMeta(store:Store) -> str:
  if store.IsHub:
    return f'AND s.region = {store.Region}'
  if store.DiscordId == settings.DATAGUILDID:
    return f'AND s.used_for_data = {True}'
  return f'AND s.discord_id = {store.DiscordId}'
"""  

def GetMetagame(game,
                format,
                start_date,
                end_date,
                store:Store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      archetype_played,
      ROUND(metagame_percent * 100, 2) AS metagame_percent,
      ROUND(win_percent * 100, 2) AS win_percent
    FROM (
      SELECT
        COALESCE(UPPER(ua.archetype_played), 'UNKNOWN') AS archetype_played,
        1.0 * sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent,
        COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
      FROM
        full_standings fp
        LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id AND UPPER(fp.player_name) = UPPER(ua.player_name)
        INNER JOIN events e ON fp.event_id = e.id
        INNER JOIN stores s ON e.discord_id = s.discord_id
      WHERE
        e.event_date BETWEEN '{start_date}' AND '{end_date}'
        {f'AND e.discord_id = {store.DiscordId}' if store.DiscordId != settings.DATAGUILDID else f'AND s.used_for_data = {True}'}
        AND e.format_id = {format.ID}
        AND e.game_id = {game.ID}
      GROUP BY
        UPPER(ua.archetype_played)
      )
    WHERE
    metagame_percent >= 0.02
    ORDER BY
    2 DESC,
    3 DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows
    