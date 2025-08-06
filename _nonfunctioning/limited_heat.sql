SELECT
  player_archetype,
  opponent_archetype,
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
  opponent_name != 'BYE'
  AND game_id = 1
  AND format_id = 1
  AND discord_id = 1210746744602890310
GROUP BY
  player_archetype,
  opponent_archetype;