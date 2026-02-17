/*I finally got a chance to look at your SQL code.  I created a snippet so maybe you will see it in the project.  

The new query calculates all weekly percentages in a single CTE instead of repeating it multiple times. Then we pivot the rows into columns in the final SELECT which is still slightly repetitive but gets our data in the same form.  Take a look at the window function (the PARTITION BY); it helps us 'slice' up the data differently than the GROUP BY. We need the count across the whole week while the GROUP BY does week/archetype.  

Anyway, I hope this is right.
*/
WITH X AS (
  SELECT
    event_date,
    INITCAP(archetype_played) AS archetype_played
  FROM events e
  INNER JOIN unique_archetypes ua ON ua.event_id = e.id
  WHERE e.discord_id = 1210746744602890310
    AND e.format_id = 1
    AND e.game_id = 1
),
weekly AS (
  SELECT
    date_trunc('week', event_date) AS week_of,
    archetype_played,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY date_trunc('week', event_date)), 2) AS meta_percent
  FROM X
  WHERE event_date >= date_trunc('week', CURRENT_DATE) - interval '9 weeks'
  GROUP BY date_trunc('week', event_date), archetype_played
)
SELECT
  archetype_played,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '1 week'  THEN meta_percent END) AS week1,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '2 weeks' THEN meta_percent END) AS week2,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '3 weeks' THEN meta_percent END) AS week3,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '4 weeks' THEN meta_percent END) AS week4,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '5 weeks' THEN meta_percent END) AS week5,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '6 weeks' THEN meta_percent END) AS week6,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '7 weeks' THEN meta_percent END) AS week7,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '8 weeks' THEN meta_percent END) AS week8,
  MAX(CASE WHEN week_of = date_trunc('week', CURRENT_DATE) - interval '9 weeks' THEN meta_percent END) AS week9
FROM weekly
GROUP BY archetype_played
ORDER BY COUNT(*) DESC, archetype_played ASC
  -- order by meta instead
  --ORDER BY SUM(meta_percent) DESC, archetype_played ASC
LIMIT 10;

--Also, if the UI does the pivoting, you could simplify that last SELECT:

WITH X AS (
  SELECT
    event_date,
    INITCAP(archetype_played) AS archetype_played
  FROM events e
  INNER JOIN unique_archetypes ua ON ua.event_id = e.id
  WHERE e.discord_id = 1210746744602890310
    AND e.format_id = 1
    AND e.game_id = 1
),
weekly AS (
  SELECT
    date_trunc('week', event_date) AS week_of,
    archetype_played,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY date_trunc('week', event_date)), 2) AS meta_percent
  FROM X
  WHERE event_date >= date_trunc('week', CURRENT_DATE) - interval '9 weeks'
  GROUP BY date_trunc('week', event_date), archetype_played
)
SELECT
  archetype_played,
  week_of,
  meta_percent
FROM weekly
ORDER BY meta_percent DESC, archetype_played ASC
LIMIT 90;
