-- Trying to get to a table that has
-- event_id, player_name, points, match win %, opponent match win %, game win %, opponent game win %
-- I think this works, though the event's OMW and OGW are different from my numbers
WITH
  individual AS (
    SELECT
      event_id,
      initcap(player_name) AS player_name,
      count(*) FILTER (
        WHERE
          upper(result) = upper('Win')
      ) AS matches_won,
      count(*) FILTER (
        WHERE
          upper(result) = upper('Draw')
      ) AS matches_drawn,
      count(*) AS total_matches,
      sum(games_won) AS games_won,
      sum(games_won + games_lost) AS total_games
    FROM
      full_pairings
    GROUP BY
      event_id,
      initcap(player_name)
  ),
  matchups AS (
    SELECT
      event_id,
      initcap(player_name) AS player_name,
      opponent_name
    FROM
      full_pairings
    ORDER BY
      event_id DESC,
      player_name
  ),
  with_opponents AS (
    SELECT
      m.event_id,
      m.player_name,
      3 * pla.matches_won + pla.matches_drawn AS points,
      pla.matches_won AS player_matches_won,
      pla.total_matches AS player_total_matches,
      pla.games_won AS player_games_won,
      pla.total_games AS player_total_games,
      m.opponent_name,
      opp.matches_won AS opp_matches_won,
      opp.total_matches AS opp_total_matches,
      opp.games_won AS opp_games_won,
      opp.total_games AS opp_total_games
    FROM
      matchups m
      INNER JOIN individual opp ON m.event_id = opp.event_id
      AND upper(opp.player_name) = upper(m.opponent_name)
      INNER JOIN individual pla ON m.event_id = pla.event_id
      AND upper(pla.player_name) = upper(m.player_name)
  )
SELECT
  event_id,
  player_name,
  cast(avg(points) AS int) AS points,
  round(
    100 * sum(opp_matches_won) / sum(opp_total_matches),
    1
  ) AS opp_match_win_percent,
  round(
    100 * sum(player_games_won) / sum(player_total_games),
    1
  ) AS player_game_win_percent,
  round(
    100 * sum(opp_games_won) / sum(opp_total_games),
    1
  ) AS opp_game_win_percent
FROM
  with_opponents
WHERE
  event_id = 118
GROUP BY
  event_id,
  player_name
ORDER BY
  event_id DESC,
  points DESC,
  opp_match_win_percent DESC,
  player_game_win_percent DESC,
  opp_game_win_percent DESC