-- Given a store's discord_id, category_id, and channel_id
-- Select all corresponding hubs

-- !! NEED TO IMPLEMENT HUB INVITES FIRST

-- There's 3 types of hub:
-- My global hub
-- Region locked hubs (matching region and format)
-- Format locked hubs (matching region and format)

(
  SELECT
    h.discord_id,
    h.hub_name,
    h.invite
  FROM
    hubs_view h
  WHERE
    h.discord_id = 1338355654959693824 -- Instead use settings.DATAHUBID
)
UNION ALL
(
  SELECT
    h.discord_id,
    h.hub_name,
    h.invite
  FROM
    hubs_view h
    INNER JOIN format_channel_maps fcm ON fcm.discord_id = h.discord_id
  WHERE
    h.region_id = 1 --region_id
    AND fcm.format_id = 1 --format_id
)
UNION ALL
(
  SELECT
    h.discord_id,
    h.hub_name,
    h.invite
  FROM
    hubs_view h
    INNER JOIN region_channel_maps rcm ON rcm.discord_id = h.discord_id
  WHERE
    rcm.region_id = 1 --region_id
    AND h.format_lock = 1 --format_id
);