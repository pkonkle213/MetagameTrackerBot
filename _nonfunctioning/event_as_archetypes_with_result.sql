WITH A AS (
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
  )
SELECT
  rd.event_id,
  rd.player1_name as player1_name,
  A1.archetype_played AS player1_archetype,
  player1_game_wins,
  rd.player2_name as player2_name,
  A2.archetype_played AS player2_archetype,
  player2_game_wins,
  CASE
    WHEN player1_game_wins > player2_game_wins THEN 'WIN'
    WHEN player1_game_wins < player2_game_wins THEN 'LOSS'
    WHEN player1_game_wins = player2_game_wins THEN 'DRAW'
  END AS player1_result
FROM
  rounddetails rd
  LEFT JOIN A A1 ON A1.event_id = rd.event_id
    AND A1.player_name = rd.player1_name
  LEFT JOIN A A2 ON A2.event_id = rd.event_id
    AND A2.player_name = rd.player2_name
WHERE
  rd.event_id = 55  
ORDER BY
  event_id DESC,
  round_number