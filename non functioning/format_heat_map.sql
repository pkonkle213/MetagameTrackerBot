SELECT player1_archetype, player2_archetype, ROUND(100 * COUNT(CASE WHEN player1_won THEN 1 END) / COUNT(*), 2) as win_percentage
FROM (
WITH Y AS (
WITH X AS (
SELECT DISTINCT on (event_id, player_name)
  event_id, player_name, archetype_played
FROM ArchetypeSubmissions
ORDER BY event_id, player_name, id desc)
SELECT
  COALESCE(x1.archetype_played, 'UNKNOWN') AS player1_archetype,
  CASE
    WHEN COALESCE(p2.player_name, 'BYE') = 'BYE' THEN 'NONE'
  ELSE
    COALESCE(x2.archetype_played, 'UNKNOWN')
  END AS player2_archetype,
  pw.id = p1.id AS player1_won
FROM rounddetails rd
  INNER JOIN participants p1 on p1.id = rd.player1_id
  LEFT JOIN X x1 ON (x1.event_id = rd.event_id AND x1.player_name = p1.player_name)
  LEFT JOIN participants p2 on p2.id = rd.player2_id
  LEFT JOIN X x2 ON (x2.event_id = rd.event_id AND x2.player_name = p2.player_name)
  LEFT JOIN participants pw on pw.id = rd.winner_id
  LEFT JOIN X xw ON (xw.event_id = rd.event_id AND xw.player_name = pw.player_name)
)
(SELECT player1_archetype, player2_archetype, player1_won
FROM Y
WHERE player1_won IS NOT NULL
  AND player2_archetype != 'NONE'
ORDER BY player1_won desc)
UNION
(SELECT
  player2_archetype as player1_archetype,
  player1_archetype as player2_archetype,
  player1_won = FALSE as player1_won
FROM Y
WHERE player2_archetype != 'NONE'
AND player1_won IS NOT NULL)
)
WHERE player2_archetype != player1_archetype
GROUP BY player1_archetype, player2_archetype
ORDER BY player1_archetype, player2_archetype