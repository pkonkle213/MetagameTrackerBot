SELECT
  INITCAP(opponent_name) AS opponent_name,
  COUNT(*) AS matches,
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
  UPPER(player_name) = UPPER('phillip konkle')
  AND UPPER(opponent_name) != 'BYE'
GROUP BY
  INITCAP(opponent_name)
ORDER BY
  COUNT(*) DESC