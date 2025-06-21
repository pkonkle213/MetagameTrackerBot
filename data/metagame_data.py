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
    FROM
    (
    SELECT
    archetype_played,
    1.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percent,
    COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
    FROM
    (
    SELECT
    COALESCE(X.archetype_played, 'UNKNOWN') AS archetype_played,
    wins,
    losses,
    draws
    FROM
    participants p
    LEFT OUTER JOIN (
    SELECT DISTINCT ON (event_id, player_name)
    event_id,
    player_name,
    archetype_played
    FROM
    ArchetypeSubmissions
    WHERE
    reported = FALSE
    ORDER BY
    event_id,
    player_name,
    id DESC
    ) X ON X.event_id = p.event_id
    AND X.player_name = p.player_name
    INNER JOIN events e ON p.event_id = e.id
    INNER JOIN stores s ON s.discord_id = e.discord_id
    WHERE
    e.event_date BETWEEN '{start_date}' AND '{end_date}'
    {f'AND e.discord_id = {store.DiscordId}' if store else 'AND s.used_for_data = TRUE'}
    AND e.format_id = {format.ID}
    AND e.game_id = {game.ID}
    UNION ALL
    SELECT
    archetype_played,
    COUNT(
    CASE
    WHEN game_wins > game_losses THEN 1
    END
    ) AS wins,
    COUNT(
    CASE
    WHEN game_wins < game_losses THEN 1
    END
    ) AS losses,
    COUNT(
    CASE
    WHEN game_wins = game_losses THEN 1
    END
    ) AS draws
    FROM
    (
    WITH
    X AS (
    WITH
    A AS (
    SELECT DISTINCT
      ON (event_id, player_name) event_id,
      player_name,
      archetype_played
    FROM
      ArchetypeSubmissions
    WHERE
      reported = FALSE
    ORDER BY
      event_id,
      player_name,
      id DESC
    )
    SELECT
    A1.player_name AS player1_name,
    COALESCE(A1.archetype_played, 'UNKNOWN') AS player1_archetype,
    player1_game_wins,
    A2.player_name AS player2_name,
    COALESCE(A2.archetype_played, 'UNKNOWN') AS player2_archetype,
    player2_game_wins
    FROM
    rounddetails rd
    INNER JOIN events e ON rd.event_id = e.id
    INNER JOIN stores s ON e.discord_id = s.discord_id
    LEFT JOIN A A1 ON A1.event_id = rd.event_id
    AND A1.player_name = rd.player1_name
    LEFT JOIN A A2 ON A2.event_id = rd.event_id
    AND A2.player_name = rd.player2_name
    WHERE
    e.event_date BETWEEN '{start_date}' AND '{end_date}'
    {f'AND e.discord_id = {store.DiscordId}' if store else 'AND s.used_for_data = TRUE'}
    AND e.format_id = {format.ID}
    AND e.game_id = {game.ID}
    ORDER BY
    rd.event_id DESC,
    rd.round_number
    ) (
    SELECT
    player1_archetype AS archetype_played,
    player1_game_wins AS game_wins,
    player2_game_wins AS game_losses
    FROM
    X
    UNION ALL
    SELECT
    player2_archetype AS archetype_played,
    player2_game_wins AS game_wins,
    player1_game_wins AS game_losses
    FROM
    X
    )
    )
    GROUP BY
    archetype_played
    ORDER BY
    1
    )
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