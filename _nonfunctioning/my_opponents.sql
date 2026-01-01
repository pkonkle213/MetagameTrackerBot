SELECT
  INITCAP(opponent_name) as opponent_name,
  count(*) AS matches,
  ROUND(
    100.0 * count(
      CASE
        WHEN result = 'WIN' THEN 1
      END
    ) / count(*),
    2
  ) AS win_percentage
FROM
  full_pairings
WHERE
  UPPER(player_name) = 'PHILLIP KONKLE'
  AND INITCAP(opponent_name) != 'Bye'
GROUP BY
  INITCAP(opponent_name)
ORDER BY
  COUNT(*) DESC