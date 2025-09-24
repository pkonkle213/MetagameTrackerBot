import os
import psycopg2

def GetPersonalMatchups(discord_id, game, format, start_date, end_date, user_id):
  conn = psycopg2.connect(os.environ['DATABASE_URL'])
  with conn, conn.cursor() as cur:
    command = f'''
    SELECT
      UPPER(COALESCE(frr.opponent_archetype, 'UNKNOWN')) AS opponent_archetype,
      COUNT(
        CASE
          WHEN result = 'WIN' THEN 1
        END
      ) AS wins,
      COUNT(
        CASE
          WHEN result = 'LOSS' THEN 1
        END
      ) AS losses,
      COUNT(
        CASE
          WHEN result = 'DRAW' THEN 1
        END
      ) AS draws,
      COUNT(*) AS total_matches,
      ROUND(
        1.0 * COUNT(
          CASE
            WHEN result = 'WIN' THEN 1
          END
        ) / (
          COUNT(
            CASE
              WHEN result = 'WIN' THEN 1
            END
          ) + COUNT(
            CASE
              WHEN result = 'LOSS' THEN 1
            END
          ) + COUNT(
            CASE
              WHEN result = 'DRAW' THEN 1
            END
          )
        ) * 100,
        2
      ) AS win_percentage
    FROM
      full_pairings frr
      INNER JOIN events e ON e.id = frr.event_id
      INNER JOIN player_names pn ON pn.player_name = frr.player_name
      AND pn.discord_id = e.discord_id
    WHERE
      pn.submitter_id = {user_id}
      AND e.discord_id = {discord_id}
      AND UPPER(frr.opponent_name) != 'BYE'
      AND e.game_id = {game.ID}
      AND e.format_id = {format.ID}
      AND e.event_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY
      UPPER(frr.opponent_archetype)
    '''
    
    cur.execute(command)
    rows = cur.fetchall()
    return rows