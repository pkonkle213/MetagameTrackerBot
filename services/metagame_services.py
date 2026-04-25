from datetime import date
from tuple_conversions import MetagameResult, Store, Format, Game, Hub
from custom_errors import KnownError
from discord import Interaction
from data.metagame_data import GetTheMetagame
from interaction_objects import GetObjectsFromInteraction
from services.date_functions import BuildDateRange

def GetWholeMetagame(
  game:Game,
  format:Format,
  start_date:date,
  end_date:date
) -> list[MetagameResult]:
  criteria = f'''
  SELECT
    COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
    wins,
    losses,
    draws
  FROM
    full_standings fs
    LEFT JOIN unique_archetypes ua ON fs.event_id = ua.event_id
    AND UPPER(fs.player_name) = UPPER(ua.player_name)
    INNER JOIN events e ON fs.event_id = e.id
  WHERE
    e.event_date BETWEEN '{start_date}' AND '{end_date}'
    AND e.game_id = {game.id}
    AND e.format_id = {format.id}
  '''

  return GetTheMetagame(criteria)

def RegionLockedMetagame(
  hub:Hub,
  channel_id:int,
  start_date:date,
  end_date:date
) -> list[MetagameResult]:
  criteria = f'''
  SELECT
    COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
    wins,
    losses,
    draws
  FROM
    full_standings fs
    LEFT JOIN unique_archetypes ua ON fs.event_id = ua.event_id
    AND UPPER(fs.player_name) = UPPER(ua.player_name)
    INNER JOIN events e ON fs.event_id = e.id
    INNER JOIN stores_view s ON e.discord_id = s.discord_id
    INNER JOIN format_channel_maps fcm ON fcm.format_id = e.format_id
    INNER JOIN hubs_view hv ON hv.region_id = s.region_id
  WHERE
    e.event_date BETWEEN '{start_date}' AND '{end_date}'
    AND hv.discord_id = {hub.discord_id}
    AND fcm.channel_id = {channel_id}
  '''
  
  return GetTheMetagame(criteria)

def FormatLockedMetagame(
  hub:Hub,
  channel_id:int,
  start_date:date,
  end_date:date
) -> list[MetagameResult]:
  criteria = f'''
  SELECT
  COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
  wins,
  losses,
  draws
FROM
  full_standings fs
  LEFT JOIN unique_archetypes ua ON fs.event_id = ua.event_id
  AND UPPER(fs.player_name) = UPPER(ua.player_name)
  INNER JOIN events e ON fs.event_id = e.id
  INNER JOIN stores_view s ON e.discord_id = s.discord_id
  INNER JOIN region_channel_maps rcm ON rcm.region_id = s.region_id
  INNER JOIN hubs_view hv ON hv.format_lock = e.format_id
WHERE
  e.event_date BETWEEN '{start_date}' AND '{end_date}'
  AND hv.discord_id = {hub.discord_id}
  AND rcm.channel_id = {channel_id}
  '''
  
  return GetTheMetagame(criteria)

def StoreMetagame(
  store:Store,
  game:Game,
  format:Format,
  date_start:date,
  date_end:date
) -> list[MetagameResult]:
  criteria = f'''  
  SELECT
    COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,
    wins,
    losses,
    draws
  FROM
    full_standings fp
    LEFT JOIN unique_archetypes ua ON fp.event_id = ua.event_id
    AND UPPER(fp.player_name) = UPPER(ua.player_name)
    INNER JOIN events e ON fp.event_id = e.id
    INNER JOIN stores s ON e.discord_id = s.discord_id
  WHERE
    e.event_date BETWEEN '{date_start}' AND '{date_end}'
    AND s.discord_id = {store.discord_id}
    AND e.format_id = {format.id}
    AND e.game_id = {game.id}
  '''
  return GetTheMetagame(criteria)
