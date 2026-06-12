WITH player_raw_stats AS (
  -- Step 1: Calculate match points, total games won, and total games played
  SELECT 
      event_id,
      player_name,
      COUNT(*) * 3 AS total_possible_match_points,
      SUM(
          CASE 
              WHEN result = 'win' THEN 3
              WHEN result = 'draw' THEN 1
              ELSE 0
          END
      ) AS total_match_points,
      SUM(games_won) AS total_games_won,
      SUM(games_won + games_lost) AS total_games_played
  FROM your_table_name
  WHERE opponent_name IS NOT NULL AND opponent_name != 'BYE' -- Exclude Byes
  GROUP BY event_id, player_name
),

player_individual_percentages AS (
  -- Step 2: Calculate MW% and GW%, applying the 33.33% floor to both
  SELECT 
      event_id,
      player_name,
      GREATEST(
          total_match_points::FLOAT / NULLIF(total_possible_match_points, 0), 
          0.3333
      ) AS individual_mw_pct,
      GREATEST(
          total_games_won::FLOAT / NULLIF(total_games_played, 0), 
          0.3333
      ) AS individual_gw_pct
  FROM player_raw_stats
)

-- Step 3: Pull the final standings with OMW% and GW%
SELECT 
  t.event_id,
  t.player_name,
  -- Tiebreaker 1: Average of your opponents' individual Match Win Percentages
  ROUND(AVG(p_opp.individual_mw_pct)::NUMERIC, 4) AS opponent_match_win_pct,
  -- Tiebreaker 2: Your own Game Win Percentage (taken from step 2)
  ROUND(MAX(p_self.individual_gw_pct)::NUMERIC, 4) AS game_win_pct
FROM your_table_name t
-- Join 1: Fetch opponent records to calculate OMW%
JOIN player_individual_percentages p_opp 
  ON t.event_id = p_opp.event_id 
  AND t.opponent_name = p_opp.player_name
-- Join 2: Fetch the player's own pre-calculated GW% floor
JOIN player_individual_percentages p_self
  ON t.event_id = p_self.event_id
  AND t.player_name = p_self.player_name
WHERE t.opponent_name IS NOT NULL AND t.opponent_name != 'BYE'
GROUP BY t.event_id, t.player_name
ORDER BY t.event_id, opponent_match_win_pct DESC, game_win_pct DESC;
