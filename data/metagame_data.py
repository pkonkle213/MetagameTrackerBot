import settings
import os
import psycopg2

def GetMetagame(game,
                format,
                start_date,
                end_date,
                store):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      archetype_played,
      ROUND(metagame_percent * 100, 2) AS metagame_percent,
      ROUND(win_percent * 100, 2) AS win_percent,
      ROUND(metagame_percent * win_percent * 100, 2) AS Combined
    FROM (
      SELECT
        COALESCE(ua.archetype_played, 'UNKNOWN') AS archetype_played,
        1.0 * sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent,
        COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
      FROM
        fullparticipants fp
        LEFT JOIN uniquearchetypes ua ON fp.event_id = ua.event_id AND fp.player_name = ua.player_name
        INNER JOIN events e ON fp.event_id = e.id
        INNER JOIN stores s ON s.discord_id = e.discord_id
      WHERE
        e.event_date BETWEEN '{start_date}' AND '{end_date}'
        {f'AND e.discord_id = {store.DiscordId}' if store.DiscordId != settings.DATAGUILDID else 'AND s.used_for_data = TRUE'}
        AND e.format_id = {format.ID}
        AND e.game_id = {game.ID}
      GROUP BY
        archetype_played
      )
    WHERE
    metagame_percent >= 0.02
    ORDER BY
    4 DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows