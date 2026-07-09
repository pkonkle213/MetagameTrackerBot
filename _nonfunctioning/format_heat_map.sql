WITH
  limited_events AS (
    SELECT
      id
    FROM
      events
    WHERE
      event_date >= date_trunc('year', CURRENT_DATE)
      AND format_id = 1
      --AND discord_id = 1210746744602890310
  ),
  archetypes AS (
    SELECT
      initcap(archetype_played) AS archetype_played,
      1.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS meta_percent
    FROM
      unique_archetypes ua
      INNER JOIN limited_events e ON e.id = ua.event_id
    GROUP BY
      initcap(archetype_played)
    ORDER BY
      meta_percent DESC
    LIMIT
      10
  ),
  paired_up AS (
    SELECT
      a1.archetype_played AS player_archetype,
      a2.archetype_played AS opponent_archetype
    FROM
      archetypes a1
      CROSS JOIN archetypes a2
    ORDER BY
      a1.archetype_played
  ),
  matchups AS (
    SELECT
      INITCAP(ua1.archetype_played) AS player_archetype,
      INITCAP(ua2.archetype_played) AS opponent_archetype,
      fp.result
    FROM
      full_pairings fp
      INNER JOIN limited_events e ON fp.event_id = e.id
      INNER JOIN unique_archetypes ua1 ON ua1.event_id = fp.event_id
      AND upper(ua1.player_name) = upper(fp.player_name)
      INNER JOIN unique_archetypes ua2 ON ua2.event_id = fp.event_id
      AND upper(ua2.player_name) = upper(fp.opponent_name)
    WHERE
      upper(fp.opponent_name) != upper('Bye')
  ),
  matchup_stats AS (
    SELECT
      player_archetype,
      opponent_archetype,
      COUNT(*) AS total_matches,
      1.0 * COUNT(
        CASE
          WHEN result = 'WIN' THEN 1
        END
      ) / COUNT(*) AS win_percentage
    FROM
      matchups
    GROUP BY
      player_archetype,
      opponent_archetype
  )
SELECT
  pu.player_archetype,
  pu.opponent_archetype,
  COALESCE(ms.total_matches, 0) AS total_matches,
  ms.win_percentage AS win_percentage
FROM
  paired_up pu
  LEFT JOIN matchup_stats ms ON ms.player_archetype = pu.player_archetype
  AND ms.opponent_archetype = pu.opponent_archetype
ORDER BY
  total_matches DESC,
  player_archetype;