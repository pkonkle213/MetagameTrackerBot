SELECT
  player_archetype,
  opponent_archetype,
  COUNT(CASE WHEN result = 'WIN' THEN 1 END) AS wins,
  COUNT(CASE WHEN result = 'LOSS' THEN 1 END) AS losses,
  COUNT(CASE WHEN result = 'DRAW' THEN 1 END) AS draws,
  1.0 * COUNT(CASE WHEN result = 'WIN' THEN 1 END) / (COUNT(CASE WHEN result = 'WIN' THEN 1 END) + COUNT(CASE WHEN result = 'LOSS' THEN 1 END)+ COUNT(CASE WHEN result = 'DRAW' THEN 1 END)) as win_percentage
FROM
  (
    WITH
      X AS (
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
      ) (
        SELECT
          X1.archetype_played AS player_archetype,
          COALESCE(X2.archetype_played, 'BYE') AS opponent_archetype,
          CASE
            WHEN rd.player1_game_wins > player2_game_wins THEN 'WIN'
            WHEN rd.player1_game_wins = rd.player2_game_wins THEN 'DRAW'
            ELSE 'LOSS'
          END AS result
        FROM
          rounddetails rd
          LEFT JOIN X AS X1 ON X1.event_id = rd.event_id
          AND X1.player_name = rd.player1_name
          LEFT JOIN X AS X2 ON X2.event_id = rd.event_id
          AND X2.player_name = rd.player2_name
        WHERE
          X1.archetype_played != X2.archetype_played
          AND X1.archetype_played IS NOT NULL
        UNION ALL
        SELECT
          X2.archetype_played AS player_archetype,
          COALESCE(X1.archetype_played, 'BYE') AS opponent_archetype,
          CASE
            WHEN rd.player2_game_wins > player1_game_wins THEN 'WIN'
            WHEN rd.player2_game_wins = rd.player1_game_wins THEN 'DRAW'
            ELSE 'LOSS'
          END AS result
        FROM
          rounddetails rd
          LEFT JOIN X AS X1 ON X1.event_id = rd.event_id
          AND X1.player_name = rd.player1_name
          LEFT JOIN X AS X2 ON X2.event_id = rd.event_id
          AND X2.player_name = rd.player2_name
        WHERE
          rd.player2_name != 'BYE'
          AND X2.archetype_played IS NOT NULL
          AND X1.archetype_played != X2.archetype_played
      )
  )
GROUP BY
  player_archetype,
  opponent_archetype