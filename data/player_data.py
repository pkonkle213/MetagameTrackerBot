import os
import psycopg2

def GetStats(discord_id,
   game,
   format,
   user_id,
   start_date,
   end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    WITH X AS (
      SELECT
        {'f.name as format_name,' if not format else ''}
        archetype_played,
        sum(wins) AS wins,
        sum(losses) AS losses,
        sum(draws) AS draws
      FROM (
        SELECT
          event_id,
          player_name,
          wins,
          losses,
          draws
        FROM participants
        UNION
        SELECT
          event_id,
          p.player_name,
          COUNT(CASE WHEN match_result = 'WIN' THEN 1 END) AS wins,
          COUNT(CASE WHEN match_result = 'LOSS' THEN 1 END) AS losses,
          COUNT(CASE WHEN match_result = 'DRAW' THEN 1 END) AS draws
        FROM (
          SELECT
            event_id,
            player1_name AS player_name,
          CASE
            WHEN player1_game_wins > player2_game_wins THEN 'WIN'
            WHEN player1_game_wins = player2_game_wins THEN 'DRAW'
            ELSE 'LOSS'
          END AS match_result
          FROM
            rounddetails
          UNION ALL
      SELECT
        event_id,
        player2_name AS player_name,
        CASE
          WHEN player2_game_wins > player1_game_wins THEN 'WIN'
          WHEN player2_game_wins = player1_game_wins THEN 'DRAW'
          ELSE 'LOSS'
        END AS match_result
      FROM
        rounddetails
      WHERE
        player2_name != 'BYE'
      ORDER BY
        player_name
    ) p
    GROUP BY
    event_id,
    p.player_name
    UNION ALL
    SELECT
    event_id,
    player_name,
    wins,
    losses,
    draws
    FROM
    participants
    ) r
    INNER JOIN events e ON r.event_id = e.id
    INNER JOIN formats f ON f.id = e.format_id
    LEFT JOIN (
    SELECT DISTINCT
    ON (event_id, player_name) event_id,
    player_name,
    archetype_played,
    submitter_id
    FROM
    ArchetypeSubmissions
    WHERE
    reported = FALSE
    ORDER BY
    event_id,
    player_name,
    id DESC
    ) asu ON asu.event_id = r.event_id
    AND asu.player_name = r.player_name
    WHERE
    r.player_name = (
    SELECT
    player_name
    FROM
    archetypesubmissions
    WHERE
    submitter_id = {user_id}
    GROUP BY
    player_name
    ORDER BY
    COUNT(*) DESC
    LIMIT
    1
    )
    AND e.discord_id = {discord_id}
    AND e.game_id = {game.ID}
    {f'AND e.format_id = {format.ID}' if format else ''}
    AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY
    {'f.name,' if not format else ''} 
    archetype_played
    )
    SELECT
    {'format_name,' if not format else ''}
    archetype_played,
    wins,
    losses,
    draws,
    ROUND(100.0 * wins / (wins + losses + draws), 2) AS win_percentage
    FROM
    (
    (
    SELECT
    1 AS rank,
    {"' ' as format_name," if not format else ''}
    'Overall' AS archetype_played,
    sum(wins) AS wins,
    sum(losses) AS losses,
    sum(draws) AS draws
    FROM
    X
    )
    UNION
    (
    SELECT
    2 AS rank,
    {'format_name,' if not format else ''}
    archetype_played,
    wins,
    losses,
    draws
    FROM
    X
    )
    )
    ORDER BY
    rank,
    {'format_name, ' if not format else ''}
    archetype_played
    '''
    
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetTopPlayerData(discord_id,
   game_id,
   format_id,
   start_date,
   end_date):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT player_name,
    round(eventpercent * 100, 2) as eventpercent,
    round(winpercent * 100, 2) as winpercent,
    round(eventpercent * winpercent * 100, 2) as Combined
    FROM (
    SELECT p.player_name,
    COUNT(*) * 1.0 / (
    SELECT COUNT(*)
    FROM events
    WHERE game_id = {game_id}
    AND format_id = {format_id}
    AND discord_id = {discord_id}
    AND event_date BETWEEN '{start_date}' AND '{end_date}'
    ) as eventpercent,
    sum(p.wins) * 1.0 / (sum(p.wins) + sum(p.losses) + sum(p.draws)) as winpercent
    FROM participants p
    INNER JOIN events e ON e.id = p.event_id
    WHERE e.event_date BETWEEN '{start_date}' AND '{end_date}'
    AND game_id = {game_id}
    AND format_id = {format_id}
    AND discord_id = {discord_id}
    GROUP BY p.player_name
    )
    ORDER BY combined desc
    LIMIT 10
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows