(
  SELECT
    TO_CHAR(e.event_date, 'MM/DD') AS event_date,
    s.store_name,
    INITCAP(archetype_played) AS archetype_played
  FROM
    full_standings fs
    INNER JOIN events e ON fs.event_id = e.id
    INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name)
    AND pn.discord_id = e.discord_id
    INNER JOIN unique_archetypes ua ON e.id = ua.event_id
    AND UPPER(ua.player_name) = UPPER(fs.player_name)
    INNER JOIN stores_view s ON s.discord_id = e.discord_id
    INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
  WHERE
    rcm.discord_id = 1181043866833518662
    AND pn.submitter_id = 216682600322957312
    AND e.event_date < CURRENT_DATE
    AND e.format_id = 1
    AND e.game_id = 1
  ORDER BY
    e.event_date DESC
  LIMIT
    1
)
UNION ALL
(
  SELECT
    TO_CHAR(e.event_date, 'MM/DD') AS event_date,
    s.store_name,
    INITCAP(archetype_played) AS archetype_played
  FROM
    full_standings fs
    INNER JOIN events e ON fs.event_id = e.id
    INNER JOIN player_names pn ON UPPER(pn.player_name) = UPPER(fs.player_name)
    AND pn.discord_id = e.discord_id
    INNER JOIN unique_archetypes ua ON e.id = ua.event_id
    AND UPPER(ua.player_name) = UPPER(fs.player_name)
    INNER JOIN stores_view s ON s.discord_id = e.discord_id
    INNER JOIN hubs_view h ON s.region_id = h.region_id
  WHERE
    h.discord_id = 1338355654959693837
    AND pn.submitter_id = 505548744444477441
    AND e.event_date < CURRENT_DATE
    AND e.format_id = 1
    AND e.game_id = 1
  ORDER BY
    e.event_date DESC
  LIMIT
    1
);