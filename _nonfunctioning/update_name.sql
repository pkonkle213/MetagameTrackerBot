UPDATE pairings
SET
  player1_name = CASE
    WHEN player1_name = 'old_name' THEN 'new_name'
    ELSE player1_name
  END,
  player2_name = CASE
    WHEN player2_name = 'old_name' THEN 'new_name'
    ELSE player2_name
  END
WHERE
  player1_name = 'old_name'
  OR player2_name = 'old_name';

UPDATE archetype_submissions
SET
  player_name = 'new_name'
WHERE
  upper(player_name) = upper('old_name');