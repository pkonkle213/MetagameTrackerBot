SELECT DISTINCT ON (frr1.player_name, frr2.player_name)
  frr1.player_name AS p1name,
  frr2.player_name AS p2name,
  COALESCE(data.matches, 0) AS matches_observed,
  ROUND(COALESCE(data.win_percentage, .5) * 100, 2) AS p1winpercentage
FROM
  fullroundresults frr1
  CROSS JOIN fullroundresults frr2
  LEFT JOIN (
    SELECT
      frr.player_name,
      frr.opponent_name,
      COUNT(*) AS matches,
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
      ) AS win_percentage
    FROM
      fullroundresults frr
      INNER JOIN events e ON frr.event_id = e.id
    WHERE
      frr.opponent_name != 'BYE'
      AND e.game_id = 1
      AND e.format_id = 1
      AND e.discord_id = 1210746744602890310
    GROUP BY
      frr.player_name,
      frr.opponent_name
  ) AS data ON data.player_name = frr1.player_name
  AND data.opponent_name = frr2.player_name
WHERE
  frr1.player_name = 'PHILLIP KONKLE'
  AND data.matches IS NOT NULL
ORDER BY
  p1name,
  p2name;