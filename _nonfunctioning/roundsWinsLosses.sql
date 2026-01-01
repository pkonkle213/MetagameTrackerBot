SELECT
  event_id,
  COUNT(*) as NumPlayers,
  MAX(wins + losses + draws) as ROUNDS,
  COUNT(
    CASE
      WHEN losses = 0
      AND draws = 0 THEN 1
    END
  ) AS "X-0-0",
  COUNT(
    CASE
      WHEN losses = 0
      AND draws = 1 THEN 1
    END
  ) AS "X-0-1",
  COUNT(
    CASE
      WHEN losses = 1
      AND draws = 0 THEN 1
    END
  ) AS "X-1-0",
  COUNT(
    CASE
      WHEN losses = 1
      AND draws = 1 THEN 1
    END
  ) AS "X-1-1"
FROM
  full_standings fs
INNER JOIN events e ON e.id = fs.event_id
  WHERE e.discord_id != 1437606618144444448
GROUP BY
  event_id
  ORDER BY NumPlayers