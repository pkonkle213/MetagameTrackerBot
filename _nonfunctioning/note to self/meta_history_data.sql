WITH
  X AS (
    SELECT
      event_date,
      INITCAP(archetype_played) AS archetype_played
    FROM
      events e
      INNER JOIN unique_archetypes ua ON ua.event_id = e.id
    WHERE
      e.discord_id = 1210746744602890310
      AND e.format_id = 1
      AND e.game_id = 1
  )
SELECT
  INITCAP(archetype_played) AS archetype_played,
  ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
FROM
  X
WHERE
  event_date BETWEEN date_trunc('week', event_date) - interval '8 weeks' AND date_trunc('week', CURRENT_DATE)
GROUP BY
  archetype_played
ORDER BY
  2 DESC
LIMIT
  10;

WITH
  X AS (
    SELECT
      event_date,
      INITCAP(archetype_played) AS archetype_played
    FROM
      events e
      INNER JOIN unique_archetypes ua ON ua.event_id = e.id
    WHERE
      e.discord_id = 1210746744602890310
      AND e.format_id = 1
      AND e.game_id = 1
  )
SELECT
  A.archetype_played,
  B.meta_percent AS week1,
  C.meta_percent AS week2,
  D.meta_percent AS week3,
  E.meta_percent AS week4,
  F.meta_percent AS week5,
  G.meta_percent AS week6,
  H.meta_percent AS week7,
  I.meta_percent AS week8,
  J.meta_percent AS current_week
FROM
  (
    SELECT
      INITCAP(archetype_played) AS archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      event_date BETWEEN date_trunc('week', event_date) - interval '8 weeks' AND date_trunc('week', CURRENT_DATE)
    GROUP BY
      archetype_played
    ORDER BY
      2 DESC
    LIMIT
      10
  ) A
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '1 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) B ON A.archetype_played = B.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '2 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) C ON A.archetype_played = C.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '3 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) D ON A.archetype_played = D.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '4 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) E ON A.archetype_played = E.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '5 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) F ON A.archetype_played = F.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '6 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) G ON A.archetype_played = G.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '7 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) H ON A.archetype_played = H.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE) - interval '8 weeks'
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) I ON A.archetype_played = I.archetype_played
  LEFT JOIN (
    SELECT
      date_trunc('week', event_date) AS week_of,
      archetype_played,
      ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
    FROM
      X
    WHERE
      date_trunc('week', event_date) = date_trunc('week', CURRENT_DATE)
    GROUP BY
      archetype_played,
      date_trunc('week', event_date)
  ) J ON A.archetype_played = J.archetype_played
ORDER BY
  1;