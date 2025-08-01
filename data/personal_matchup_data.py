import os
import psycopg2

def GetPersonalMatchups(discord_id, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      COALESCE(asu.archetype_played, 'UNKNOWN') AS opponent_archetype,
      sum(wins) AS wins,
      sum(losses) AS losses,
      sum(draws) AS draws,
      COUNT(*) AS total_matches,
      ROUND(
        100.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)),
        2
      ) AS win_percentage
    FROM
      (
        SELECT
          event_id,
          player1_name AS player_name,
          player2_name AS opponent_name,
          CASE
            WHEN player1_game_wins > player2_game_wins THEN 1
            ELSE 0
          END AS WINS,
          CASE
            WHEN player1_game_wins < player2_game_wins THEN 1
            ELSE 0
          END AS LOSSES,
          CASE
            WHEN player1_game_wins = player2_game_wins THEN 1
            ELSE 0
          END AS DRAWS
        FROM
          rounddetails
        UNION ALL
        SELECT
          event_id,
          player2_name AS player_name,
          player1_name AS opponent_name,
          CASE
            WHEN player2_game_wins > player1_game_wins THEN 1
            ELSE 0
          END AS WINS,
          CASE
            WHEN player2_game_wins < player1_game_wins THEN 1
            ELSE 0
          END AS LOSSES,
          CASE
            WHEN player2_game_wins = player1_game_wins THEN 1
            ELSE 0
          END AS DRAWS
        FROM
          rounddetails
      ) rd
      INNER JOIN events e ON rd.event_id = e.id
      LEFT JOIN uniquearchetypes asu ON asu.event_id = rd.event_id
      AND rd.opponent_name = asu.player_name
      INNER JOIN playernames pn ON pn.discord_id = e.discord_id
      AND pn.player_name = rd.player_name
    WHERE
      opponent_name != 'BYE'
      AND e.discord_id = {discord_id}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.format_id = {format.ID}
      AND e.game_id = {game.ID}
      AND pn.submitter_id = {user_id}
    GROUP BY
      asu.archetype_played
    ORDER BY
      asu.archetype_played            
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows