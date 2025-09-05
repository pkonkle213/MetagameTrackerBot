SELECT
  e.event_date,
  s.store_name,
  g.name,
  f.name,
  frr.round_number,
  frr.player_archetype AS your_archetype,
  frr.opponent_archetype,
  frr.result
FROM
  full_pairings frr
  INNER JOIN events e ON e.id = frr.event_id
  INNER JOIN stores s ON s.discord_id = e.discord_id
  INNER JOIN formats f ON f.id = e.format_id
  INNER JOIN cardgames g ON g.id = e.game_id
  INNER JOIN player_names pn ON s.discord_id = pn.discord_id
  AND pn.player_name = frr.player_name
WHERE
  pn.submitter_id = {submitter_id}
ORDER BY
  e.event_date DESC,
  frr.round_number