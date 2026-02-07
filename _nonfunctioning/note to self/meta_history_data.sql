--Select the top 10 archetypes played during the ENTIRE span
SELECT
  INITCAP(archetype_played) AS archetype_played,
  ROUND(100.0 * COUNT(*) / COUNT(*) OVER(), 2) as meta_percent
FROM
  events e
  INNER JOIN unique_archetypes ua ON ua.event_id = e.id
WHERE
  e.discord_id = 1210746744602890310
  AND e.format_id = 1
  AND e.game_id = 1
  AND e.event_date BETWEEN date_trunc('week', e.event_date) - interval '8 weeks' AND date_trunc('week', CURRENT_DATE)
GROUP BY archetype_played
  ORDER BY 2 DESC
  LIMIT 10
  ;

-- Use this to find data in a week. Adjust interval for X weeks
SELECT
  date_trunc('week', e.event_date) AS week_of,
  INITCAP(ua.archetype_played) AS archetype_played,
  ROUND(100.0 * COUNT(*) / COUNT(*) OVER (), 2) AS meta_percent
FROM
  events e
  INNER JOIN unique_archetypes ua ON ua.event_id = e.id
WHERE
  date_trunc('week', e.event_date) = date_trunc('week', CURRENT_DATE) - interval '1 weeks'
  AND e.discord_id = 1210746744602890310
  AND e.format_id = 1
  AND e.game_id = 1
GROUP BY
  INITCAP(archetype_played),
  date_trunc('week', e.event_date);

--Need to first figure out event ids, maybe that will limit the times I need 'where' in the statement(s)
--...maybe not idk