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
      ROUND(win_percent * 100, 2) AS win_percent
    FROM (
      SELECT
        COALESCE(ua.archetype_played, 'Unknown') AS archetype_played,
        1.0 * sum(fp.wins) / (sum(fp.wins) + sum(fp.losses) + sum(fp.draws)) AS win_percent,
        COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
      FROM
        fullparticipants fp
        LEFT JOIN uniquearchetypes ua ON fp.event_id = ua.event_id AND fp.player_name = ua.player_name
        INNER JOIN events e ON fp.event_id = e.id
        INNER JOIN stores s ON e.discord_id = s.discord_id
      WHERE
        e.event_date BETWEEN '{start_date}' AND '{end_date}'
        {f'AND e.discord_id = {store.DiscordId}' if store.DiscordId != settings.DATAGUILDID else ''}
        AND e.format_id = {format.ID}
        AND e.game_id = {game.ID}
        AND s.isapproved = {True}
      GROUP BY
        archetype_played
      )
    WHERE
    metagame_percent >= 0.02
    ORDER BY
    2 DESC
    '''

    cur.execute(command)
    rows = cur.fetchall()
    return rows
    