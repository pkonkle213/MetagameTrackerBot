--How is this prettier? This is ugly...

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
          COALESCE(A1.archetype_played, 'UNKNOWN') AS player1_archetype,
          player1_game_wins,
          COALESCE(A2.archetype_played, 'UNKNOWN') AS player2_archetype,
          player2_game_wins
        FROM
          rounddetails rd
          LEFT JOIN A A1 ON A1.event_id = rd.event_id
            AND A1.player_name = rd.player1_name
          LEFT JOIN A A2 ON A2.event_id = rd.event_id
            AND A2.player_name = rd.player2_name
        --WHERE rd.event_id = 55
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
  wins DESC,
  draws DESC