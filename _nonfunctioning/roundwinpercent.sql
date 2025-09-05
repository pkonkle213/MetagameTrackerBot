SELECT
  p1archetype AS archetype,
  sum(metawinpercent) AS adjustedwinpercent
FROM
  (
    SELECT DISTINCT
      ON (frr1.player_archetype, frr2.player_archetype) frr1.player_archetype AS p1archetype,
      frr2.player_archetype AS p2archetype,
      COALESCE(data.win_percentage, .5) * Metagame.Metagame_Percent AS metawinpercent
    FROM
      full_pairings frr1
      CROSS JOIN full_pairings frr2
      LEFT JOIN (
        SELECT
          frr.player_archetype,
          frr.opponent_archetype,
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
          AND e.event_date BETWEEN '2025-06-10' AND '2025-08-31'
        GROUP BY
          frr.player_archetype,
          frr.opponent_archetype
      ) AS data ON data.player_archetype = frr1.player_archetype
      AND data.opponent_archetype = frr2.player_archetype
      LEFT JOIN (
        SELECT
          COALESCE(ua.archetype_played, 'UNKNOWN') AS archetype_played,
          COUNT(*) * 1.0 / SUM(count(*)) OVER () AS Metagame_Percent
        FROM
          full_standings fp
          LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id
          AND fp.player_name = ua.player_name
          INNER JOIN events e ON fp.event_id = e.id
        WHERE
          e.game_id = 1
          AND e.format_id = 1
          AND e.discord_id = 1210746744602890310
          AND e.event_date BETWEEN '2025-06-10' AND '2025-08-31'
        GROUP BY
          archetype_played
      ) AS Metagame ON frr2.player_archetype = Metagame.archetype_played
    ORDER BY
      p1archetype,
      p2archetype
  )
GROUP BY
  p1archetype;