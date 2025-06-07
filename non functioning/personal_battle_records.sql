SELECT opponent_name,
  COUNT(CASE WHEN my_result = TRUE THEN 1 END) AS wins,
  COUNT(*) AS total,
  ROUND(100.0 * COUNT(CASE WHEN my_result = TRUE THEN 1 END) / COUNT(*), 2) AS win_percentage
FROM (
SELECT 
  CASE
   WHEN player2_name = 'PHILLIP KONKLE' THEN player1_name
   WHEN player1_name = 'PHILLIP KONKLE' THEN player2_name
  END AS opponent_name,
  CASE
   WHEN player1_name = 'PHILLIP KONKLE' AND player1_won = TRUE THEN TRUE
   WHEN player2_name = 'PHILLIP KONKLE' AND player1_won = FALSE THEN TRUE
  ELSE
    FALSE
  END AS my_result
FROM (
  WITH X AS (SELECT DISTINCT on (event_id, player_name)
    event_id, player_name, archetype_played
  FROM ArchetypeSubmissions
  ORDER BY event_id, player_name, id desc)
  SELECT
    p1.player_name as player1_name,
    COALESCE(p2.player_name, 'BYE') as player2_name,
    pw.id = p1.id AS player1_won
  FROM rounddetails rd
    INNER JOIN participants p1 on p1.id = rd.player1_id
    LEFT JOIN X x1 ON (x1.event_id = rd.event_id AND x1.player_name = p1.player_name)
    LEFT JOIN participants p2 on p2.id = rd.player2_id
    LEFT JOIN X x2 ON (x2.event_id = rd.event_id AND x2.player_name = p2.player_name)
    LEFT JOIN participants pw on pw.id = rd.winner_id
    LEFT JOIN X xw ON (xw.event_id = rd.event_id AND xw.player_name = pw.player_name)
)
WHERE player1_name = 'PHILLIP KONKLE' OR player2_name = 'PHILLIP KONKLE')
WHERE opponent_name != 'BYE'
GROUP BY opponent_name