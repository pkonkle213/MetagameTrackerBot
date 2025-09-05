SELECT DISTINCT ON (frr1.player_archetype, frr2.player_archetype)
  frr1.player_archetype AS p1archetype,
  frr2.player_archetype AS p2archetype,
  COALESCE(data.matches, 0) AS matches_observed,
  ROUND(COALESCE(data.win_percentage, .5) * 100, 2) AS p1winpercentage
FROM
  full_pairings frr1
  CROSS JOIN full_pairings frr2
  LEFT JOIN (
    SELECT
      frr.player_archetype,
      frr.opponent_archetype,
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
      full_pairings frr
      INNER JOIN events e ON frr.event_id = e.id
    WHERE
      frr.opponent_name != 'BYE'
      AND e.game_id = 1
      AND e.format_id = 1
      AND e.discord_id = 1210746744602890310
  AND e.event_date BETWEEN '2023-01-01' AND '2023-12-31'
    GROUP BY
      frr.player_archetype,
      frr.opponent_archetype
  ) AS data ON data.player_archetype = frr1.player_archetype
  AND data.opponent_archetype = frr2.player_archetype
ORDER BY
  p1archetype,
  p2archetype;