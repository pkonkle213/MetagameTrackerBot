SELECT
  player_archetype,
  opponent_archetype,
  COUNT(CASE WHEN result = 'WIN' THEN 1 END) AS wins,
  COUNT(CASE WHEN result = 'LOSS' THEN 1 END) AS losses,
  COUNT(CASE WHEN result = 'DRAW' THEN 1 END) AS draws,
  1.0 * COUNT(CASE WHEN result = 'WIN' THEN 1 END) / (COUNT(CASE WHEN result = 'WIN' THEN 1 END) + COUNT(CASE WHEN result = 'LOSS' THEN 1 END)+ COUNT(CASE WHEN result = 'DRAW' THEN 1 END)) as win_percentage
FROM
  fullroundresults
WHERE
  opponent_name != 'BYE'
GROUP BY
  player_archetype,
  opponent_archetype