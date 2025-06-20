import os
import psycopg2

def GetPersonalMatchups(discord_id, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      COALESCE(asu.archetype_played, 'UNKNOWN') AS opponent_archetype,
      COUNT(CASE WHEN player_game_wins > player_game_losses THEN 1 END) AS wins,
      COUNT(CASE WHEN player_game_wins = player_game_losses THEN 1 END) AS draws,
      COUNT(CASE WHEN player_game_wins < player_game_losses THEN 1 END) AS losses,
      COUNT(*) AS total_matches,
      ROUND(100.0 * COUNT(CASE WHEN player_game_wins > player_game_losses THEN 1 END) / (COUNT(CASE WHEN player_game_wins > player_game_losses THEN 1 END) + COUNT(CASE WHEN player_game_wins = player_game_losses THEN 1 END) + COUNT(CASE WHEN player_game_wins < player_game_losses THEN 1 END)), 2) as win_percentage
    FROM
      (
        SELECT
          event_id,
          player1_name AS player_name,
          player2_name AS opponent_name,
          player1_game_wins AS player_game_wins,
          player2_game_wins AS player_game_losses
        FROM
          rounddetails
        UNION ALL
        SELECT
          event_id,
          player2_name AS player_name,
          player1_name AS opponent_name,
          player2_game_wins AS player_game_wins,
          player1_game_wins AS player_game_losses
        FROM
          rounddetails
      ) rd
      INNER JOIN events e ON rd.event_id = e.id
      LEFT JOIN (
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
      ) asu ON asu.event_id = rd.event_id
      AND rd.opponent_name = asu.player_name
    WHERE
      rd.player_name = (SELECT
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
              1)
      AND opponent_name != 'BYE'
      AND e.discord_id = {discord_id}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
      AND e.format_id = {format.ID}
      AND e.game_id = {game.ID}
    GROUP BY
      asu.archetype_played
    ORDER BY
      asu.archetype_played
    '''
    print('Command:', command)
    cur.execute(command)
    rows = cur.fetchall()
    return rows