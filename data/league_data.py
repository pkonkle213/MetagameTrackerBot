from custom_errors import KnownError
from psycopg import AsyncConnection
from settings import DATABASE_URL
from datetime import date
from psycopg.rows import class_row, scalar_row
from tuple_conversions import League, TopPlayers, PlayerStanding, LeaderboardRace


async def GetLeague(league_id: int) -> League:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(League)) as cur,
    ):
        command = """
        SELECT *
        FROM leagues_view
        WHERE id = %s
        """

        await cur.execute(command, [league_id])
        row = await cur.fetchone()
        if not row:
            raise KnownError("No league found with that id")
        return row


async def GetActiveLeagues(
    discord_id: int, game_id: int, format_id: int
) -> list[League]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(League)) as cur,
    ):
        command = """
        SELECT *
        FROM leagues
        WHERE discord_id = %s
        AND game_id = %s
        AND format_id = %s
        AND start_date <= CURRENT_DATE
        AND end_date >= CURRENT_DATE
        ORDER BY end_date DESC, start_date DESC
        """

        await cur.execute(command, [discord_id, game_id, format_id])
        rows = await cur.fetchall()
        return rows


async def GetHubPlayerStanding(league: League, user_id: int) -> PlayerStanding:
    results = f"""
    SELECT
      INITCAP(fs.player_name) AS player_name,
      e.discord_id,
      wins,
      losses,
      draws
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
      INNER JOIN hub_league_stores hls ON e.discord_id = hls.store_discord_id
      INNER JOIN leagues l ON l.id = hls.league_id
      AND e.event_date >= l.start_date
      AND e.event_date <= l.end_date
    WHERE
      hls.league_id = {league.id}
    """

    standing = await GetPlayerStanding(results, user_id)
    return standing


async def GetStorePlayerStanding(league: League, user_id: int) -> PlayerStanding:
    results = f"""
    SELECT
      INITCAP(fs.player_name) AS player_name,
      e.discord_id,
      wins,
      losses,
      draws
    FROM
      full_standings fs
      INNER JOIN events e ON fs.event_id = e.id
    WHERE
      e.league_id = {league.id}
    """

    standing = await GetPlayerStanding(results, user_id)
    return standing


async def GetPlayerStanding(results: str, user_id: int) -> PlayerStanding:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(PlayerStanding)) as cur,
    ):
        command = f"""
        WITH
          league_results AS (
            {results}
          ),
          name_translate AS (
              SELECT
                COALESCE(pn.submitter_id::text, lr.player_name) AS player_name,
                wins,
                losses,
                draws
              FROM
                league_results lr
                LEFT JOIN player_names pn ON pn.discord_id = lr.discord_id
                AND UPPER(pn.player_name) = UPPER(lr.player_name)
          ),
          grouped AS (
            SELECT
              player_name,
              (3 * SUM(wins) + SUM(draws)) AS points,
              ROUND(
                100.0 * SUM(wins) / (SUM(wins) + SUM(losses) + SUM(draws)),
                2
              ) AS win_percent
            FROM
              name_translate
            GROUP BY
              player_name
            ORDER BY
              points DESC,
              win_percent DESC,
              player_name
          ),
          ranked AS (
            SELECT
              *,
              ROW_NUMBER() OVER () AS rank
            FROM
              grouped
          )
        SELECT
          points,
          win_percent,
          rank
        FROM
          ranked r
        WHERE
          r.player_name = {user_id}::text          
        """

        await cur.execute(command)  # type: ignore[arg-type]
        row = await cur.fetchone()
        if not row:
            raise KnownError("Unable to find player standing")
        return row


async def GetLeaderboardTimeLapse(league: League) -> list[LeaderboardRace]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(LeaderboardRace)) as cur,
    ):
        command = """
        SELECT
            e.event_date,
            INITCAP(fs.player_name) as player_name,
            3 * wins + draws AS points
        FROM
            full_standings fs
            INNER JOIN events e ON fs.event_id = e.id
        WHERE
            e.league_id = %s
        ORDER BY
            e.event_date
        """

        await cur.execute(command, [league.id])
        rows = await cur.fetchall()
        return rows


async def GetFullLeagueLeaderboard(league: League) -> list[TopPlayers]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(TopPlayers)) as cur,
    ):
        command = """
        SELECT
            rank,
            player_name,
            points,
            win_percent
        FROM
            league_leaderboards
        WHERE
            league_id = %s
        """

        await cur.execute(command, [league.id])
        rows = await cur.fetchall()
        return rows


async def GetHubFullLeagueLeaderboard(league: League) -> list[TopPlayers]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(TopPlayers)) as cur,
    ):
        command = """
        WITH
          all_events AS (
            SELECT
              date_trunc('week', event_date) AS week_start,
              INITCAP(fs.player_name) AS player_name,
              3 * wins + draws AS event_points,
              wins,
              losses,
              draws
            FROM
              leagues l
              INNER JOIN hub_league_stores hls ON hls.league_id = l.id
              INNER JOIN events e ON e.discord_id = hls.store_discord_id
              AND e.event_date >= l.start_date
              AND e.event_date <= l.end_date
              AND e.format_id = l.format_id
              INNER JOIN full_standings fs ON fs.event_id = e.id
            WHERE
              l.id = %s
            ORDER BY
              week_start,
              player_name
          ),
          weekly_scores AS (
            SELECT
              week_start,
              player_name,
              LEAST(9, max(event_points)) AS week_points,
              sum(wins) AS wins,
              sum(losses) AS losses,
              sum(draws) AS draws
            FROM
              all_events
            GROUP BY
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
              100.0 * sum(wins) / (sum(wins) + sum(losses) + sum(draws)) AS win_percent
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
          total_points AS points,
          ROUND(win_percent, 2) AS win_percent
        FROM
          grouped
        """

        await cur.execute(command, [league.id])
        rows = await cur.fetchall()
        return rows


async def GetLeagues(discord_id: int, game_id: int, format_id: int) -> list[League]:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=class_row(League)) as cur,
    ):
        command = """
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
            created_by,
            last_updated,
            created_date,
            updated_by,
            store_ids
        FROM
            leagues_view l
        WHERE
            discord_id = %s
            AND game_id = %s
            AND format_id = %s
        ORDER BY
            end_date DESC, start_date DESC
        """

        await cur.execute(command, [discord_id, game_id, format_id])
        rows = await cur.fetchall()
        if not rows or len(rows) == 0:
            raise KnownError("No leagues found")
        return rows


async def UpdateLeague(
    league_id: int,
    league_name: str,
    description: str,
    start_date: date,
    end_date: date,
    top_cut: int,
    user_id: int,
) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
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
        RETURNING id
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

        await cur.execute(command, criteria)
        row = await cur.fetchone()
        if not row:
            raise KnownError("Unable to update league")
        return row


async def InsertLeague(
    league_name: str,
    description: str,
    start_date: date,
    end_date: date,
    top_cut: int,
    store_id: int,
    game_id: int,
    format_id: int,
    user_id: int,
) -> int:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor(row_factory=scalar_row) as cur,
    ):
        command = """
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
        RETURNING id
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

        await cur.execute(command, criteria)
        league_id = await cur.fetchone()
        if not league_id:
            raise KnownError("Unable to create league")

        return league_id
