from custom_errors import KnownError
import psycopg
from settings import DATABASE_URL
from datetime import date
from psycopg.rows import class_row
from tuple_conversions import League, TopPlayers, PlayerStanding, LeaderboardRace, HubLeague


def GetActiveLeagues(discord_id: int, game_id: int, format_id: int) -> list[League]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(League)) as cur:
        command = f"""
        SELECT *
        FROM leagues
        WHERE discord_id = %s
        AND game_id = %s
        AND format_id = %s
        AND start_date <= CURRENT_DATE
        AND end_date >= CURRENT_DATE
        ORDER BY end_date DESC, start_date DESC
        """

        cur.execute(command, [discord_id, game_id, format_id])
        rows = cur.fetchall()
        return rows


def GetPlayerStanding(league: League, user_id: int, discord_id: int) -> PlayerStanding:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(PlayerStanding)) as cur:
        command = f"""
        WITH
          X AS (
            SELECT
              INITCAP(player_name) AS player_name,
              wins,
              losses,
              draws
            FROM
              full_standings fs
              INNER JOIN events e ON fs.event_id = e.id
              INNER JOIN stores_view s ON e.discord_id = s.discord_id
            WHERE
              e.league_id = {league.id}
          ),
          Y AS (
            SELECT
              player_name,
              (3 * SUM(wins) + SUM(draws)) AS points,
              ROUND(
                100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)),
                2
              ) AS win_percent
            FROM
              X
            GROUP BY
              player_name
            ORDER BY
              2 DESC,
              3 DESC,
              1
          ),
          Z AS (
            SELECT
              *,
              ROW_NUMBER() OVER () AS rank
            FROM
              Y
          )
        SELECT
          points,
          win_percent,
          rank
        FROM
          Z
          LEFT JOIN player_names pn ON UPPER(Z.player_name) = UPPER(pn.player_name)
        WHERE
          pn.submitter_id = {user_id}
          AND pn.discord_id = {discord_id}
        """

        cur.execute(command)
        row = cur.fetchone()
        if not row:
            raise KnownError("Unable to find player standing")

        return row


def GetLeaderboardTimeLapse(league: League) -> list[LeaderboardRace]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(LeaderboardRace)) as cur:
        command = f"""
        SELECT
          e.event_date,
          INITCAP(fs.player_name) as player_name,
          3 * wins + draws AS points
        FROM
          full_standings fs
          INNER JOIN events e ON fs.event_id = e.id
        WHERE e.league_id = {league.id}
        ORDER BY e.event_date
        """

        cur.execute(command)
        rows = cur.fetchall()
        return rows


def GetFullLeagueLeaderboard(league: League) -> list[TopPlayers]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(TopPlayers)) as cur:
        command = f"""
        SELECT
          rank,
          player_name,
          points,
          win_percent
        FROM
          store_league_leaderboards
        WHERE
          league_id = {league.id}
        """
        cur.execute(command)
        rows = cur.fetchall()
        return rows

def GetHubFullLeagueLeaderboard(league:HubLeague) -> list[TopPlayers]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(TopPlayers)) as cur:
    command = f"""
    WITH
      weekly_scores AS (
        SELECT
          date_trunc('week', event_date) AS week_start,
          INITCAP(player_name) AS player_name,
          LEAST(9, sum(3 * wins + draws)) AS week_points,
          sum(wins) AS wins,
          sum(losses) AS losses,
          sum(draws) AS draws
        FROM
          leagues l
          INNER JOIN hub_league_stores hls ON hls.league_id = l.id
          INNER JOIN events e ON e.discord_id = hls.store_discord_id
          AND e.event_date >= l.start_date
          AND e.event_date <= l.end_date
          AND e.format_id = l.format_id
          INNER JOIN full_standings fs ON fs.event_id = e.id
        WHERE
          l.id = {league.id}
        GROUP BY
          date_trunc('week', event_date),
          initcap(player_name)
        ORDER BY
          week_start,
          player_name
      ),
      top_ten AS (
        SELECT
          player_name,
          week_points,
          wins,
          losses,
          draws,
          ROW_NUMBER() OVER (
            PARTITION BY
              player_name
            ORDER BY
              week_points DESC
          ) AS rank
        FROM
          weekly_scores
      ),
      grouped AS (
        SELECT
          player_name,
          sum(week_points) AS total_points,
          1.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percent
        FROM
          top_ten
        WHERE
          rank <= 12
        GROUP BY
          player_name
      )
    SELECT
      ROW_NUMBER() OVER (
        ORDER BY
          total_points DESC,
          win_percent DESC,
          player_name
      ) AS rank,
      player_name,
      total_points as points,
      win_percent
    FROM
      grouped
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetHubLeagueLeaderboard(league:League) -> list[TopPlayers]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(TopPlayers)) as cur:
    command = f"""
    WITH
      weekly_scores AS (
        SELECT
          date_trunc('week', event_date) AS week_start,
          INITCAP(player_name) AS player_name,
          LEAST(9, sum(3 * wins + draws)) AS week_points,
          sum(wins) AS wins,
          sum(losses) AS losses,
          sum(draws) AS draws
        FROM
          leagues l
          INNER JOIN hub_league_stores hls ON hls.league_id = l.id
          INNER JOIN events e ON e.discord_id = hls.store_discord_id
          AND e.event_date >= l.start_date
          AND e.event_date <= l.end_date
          AND e.format_id = l.format_id
          INNER JOIN full_standings fs ON fs.event_id = e.id
        WHERE
          l.id = {league.id}
        GROUP BY
          date_trunc('week', event_date),
          initcap(player_name)
        ORDER BY
          week_start,
          player_name
      ),
      top_ten AS (
        SELECT
          player_name,
          week_points,
          wins,
          losses,
          draws,
          ROW_NUMBER() OVER (
            PARTITION BY
              player_name
            ORDER BY
              week_points DESC
          ) AS rank
        FROM
          weekly_scores
      ),
      grouped AS (
        SELECT
          player_name,
          sum(week_points) AS total_points,
          1.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percent
        FROM
          top_ten
        WHERE
          rank <= 12
        GROUP BY
          player_name
      )
    SELECT
      ROW_NUMBER() OVER (
        ORDER BY
          total_points DESC,
          win_percent DESC,
          player_name
      ) AS rank,
      player_name,
      total_points as points,
      win_percent
    FROM
      grouped
    LIMIT
      8
    """

    cur.execute(command)
    rows = cur.fetchall()
    return rows

def GetLeagueLeaderboard(league: League) -> list[TopPlayers]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(TopPlayers)) as cur:
        command = f"""
        SELECT
          rank,
          player_name,
          points,
          win_percent
        FROM
          store_league_leaderboards
        WHERE
          league_id = {league.id}
        LIMIT
          {league.top_cut}
        """
      
        cur.execute(command)
        rows = cur.fetchall()
        return rows

def GetHubLeagues(
  discord_id: int,
  game_id: int,
  format_id:int
) -> list[HubLeague]:
  conn = psycopg.connect(DATABASE_URL)
  with conn, conn.cursor(row_factory=class_row(HubLeague)) as cur:
    command = f"""
    SELECT
      id,
      discord_id,
      game_id,
      format_id,
      name,
      start_date,
      end_date,
      top_cut,
      description,
      store_discord_id AS store_ids
    FROM
      leagues l
      LEFT JOIN hub_league_stores hls ON l.id = hls.league_id
    WHERE
      discord_id = {discord_id}
      AND game_id = {game_id}
      AND format_id = {format_id}
    """

    cur.execute(command)
    rows = cur.fetchall()
    if not rows or len(rows) == 0:
      raise KnownError('No leagues found')
    return rows
    

def GetLeagues(discord_id: int, game_id: int, format_id: int) -> list[League]:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(League)) as cur:
        command = f"""
        SELECT
          *
        FROM
          leagues
        WHERE
          discord_id = %s
          AND game_id = %s
          AND format_id = %s
        ORDER BY end_date DESC, start_date DESC
        """
        cur.execute(command, [discord_id, game_id, format_id])
        rows = cur.fetchall()
        if not rows or len(rows) == 0:
          raise KnownError('No leagues found')
        return rows


def UpdateLeague(
    league_id: int,
    league_name: str,
    description: str,
    start_date: date,
    end_date: date,
    top_cut: int,
    user_id: int,
) -> League:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(League)) as cur:
        command = f"""
        UPDATE leagues
        SET
          name = %s,
          description = %s,
          start_date = %s,
          end_date = %s,
          top_cut = %s,
          last_updated = NOW(),
          updated_by = %s
        WHERE id = %s
        RETURNING *
        """

        criteria = [
            league_name,
            description,
            start_date,
            end_date,
            top_cut,
            user_id,
            league_id,
        ]
        cur.execute(command, criteria)
        row = cur.fetchone()
        if not row:
            raise KnownError("Unable to update league")
        return row


def InsertLeague(
    league_name: str,
    description: str,
    start_date: date,
    end_date: date,
    top_cut: int,
    store_id: int,
    game_id: int,
    format_id: int,
    user_id: int,
) -> League:
    conn = psycopg.connect(DATABASE_URL)
    with conn, conn.cursor(row_factory=class_row(League)) as cur:
        command = f"""
        INSERT INTO leagues (
          name,
          description,
          start_date,
          end_date,
          top_cut,
          discord_id,
          game_id,
          format_id,
          created_by,
          created_date
        )
        VALUES (
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          NOW()
        )
        RETURNING *
        """

        criteria = [
            league_name,
            description,
            start_date,
            end_date,
            top_cut,
            store_id,
            game_id,
            format_id,
            user_id,
        ]
        cur.execute(command, criteria)
        row = cur.fetchone()
        if not row:
            raise KnownError("Unable to create league")
        return row
