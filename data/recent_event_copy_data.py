from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from psycopg import AsyncConnection

from settings import DATABASE_URL


COPY_WINDOW_WEEKS = 12

_PREVIEW_QUERY = """
WITH candidate_events AS MATERIALIZED (
    SELECT id, event_date
    FROM public.events
    WHERE event_date >= CURRENT_DATE - (%s * 7)
      AND event_date <= CURRENT_DATE
      AND discord_id IS DISTINCT FROM %s
)
SELECT
    COALESCE(
        (SELECT array_agg(id ORDER BY id) FROM candidate_events),
        ARRAY[]::integer[]
    ) AS event_ids,
    (SELECT count(*) FROM candidate_events) AS event_count,
    (
        SELECT count(*)
        FROM public.pairings p
        JOIN candidate_events e ON e.id = p.event_id
    ) AS pairing_count,
    (
        SELECT count(*)
        FROM public.archetype_submissions a
        JOIN candidate_events e ON e.id = a.event_id
    ) AS submission_count,
    (SELECT min(event_date) FROM candidate_events) AS first_event_date,
    (SELECT max(event_date) FROM candidate_events) AS last_event_date,
    EXISTS (
        SELECT 1 FROM public.stores WHERE discord_id = %s
    ) AS target_is_store,
    EXISTS (
        SELECT 1 FROM public.discords WHERE discord_id = %s
    ) AS target_is_registered,
    (
        SELECT store_name FROM public.stores WHERE discord_id = %s
    ) AS target_store_name,
    (
        SELECT count(*)
        FROM public.events
        WHERE discord_id = %s
          AND event_date >= CURRENT_DATE - (%s * 7)
          AND event_date <= CURRENT_DATE
    ) AS existing_target_event_count
"""


@dataclass(frozen=True)
class RecentEventCopyPreview:
    target_discord_id: int
    event_ids: tuple[int, ...]
    event_count: int
    pairing_count: int
    submission_count: int
    first_event_date: date | None
    last_event_date: date | None
    target_is_store: bool
    target_is_registered: bool
    target_store_name: str | None
    existing_target_event_count: int


@dataclass(frozen=True)
class RecentEventCopyResult:
    event_count: int
    pairing_count: int
    submission_count: int


async def _load_preview(cursor, target_discord_id: int) -> RecentEventCopyPreview:
    await cursor.execute(
        _PREVIEW_QUERY,
        (
            COPY_WINDOW_WEEKS,
            target_discord_id,
            target_discord_id,
            target_discord_id,
            target_discord_id,
            target_discord_id,
            COPY_WINDOW_WEEKS,
        ),
    )
    row = await cursor.fetchone()
    (
        event_ids,
        event_count,
        pairing_count,
        submission_count,
        first_event_date,
        last_event_date,
        target_is_store,
        target_is_registered,
        target_store_name,
        existing_target_event_count,
    ) = row
    return RecentEventCopyPreview(
        target_discord_id=target_discord_id,
        event_ids=tuple(event_ids or ()),
        event_count=event_count,
        pairing_count=pairing_count,
        submission_count=submission_count,
        first_event_date=first_event_date,
        last_event_date=last_event_date,
        target_is_store=target_is_store,
        target_is_registered=target_is_registered,
        target_store_name=target_store_name,
        existing_target_event_count=existing_target_event_count,
    )


async def PreviewRecentEventCopy(
    target_discord_id: int,
) -> RecentEventCopyPreview:
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        return await _load_preview(cur, target_discord_id)


async def CopyRecentEventsToStore(
    preview: RecentEventCopyPreview,
) -> RecentEventCopyResult:
    target_discord_id = preview.target_discord_id

    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"
                )
                await cur.execute(
                    """
                    LOCK TABLE public.archetype_submissions,
                               public.events,
                               public.pairings
                    IN ACCESS EXCLUSIVE MODE
                    """
                )

                current = await _load_preview(cur, target_discord_id)
                if not current.target_is_registered or not current.target_is_store:
                    raise ValueError(
                        "The destination must exist in both discords and stores."
                    )
                if current.existing_target_event_count:
                    raise ValueError(
                        "The destination already has events in the last 12 weeks; "
                        "refusing a duplicate copy."
                    )
                if current.event_ids != preview.event_ids:
                    raise ValueError(
                        "The source events changed after preview. Run the command "
                        "again to review an updated preview."
                    )
                if (
                    current.event_count != preview.event_count
                    or current.pairing_count != preview.pairing_count
                    or current.submission_count != preview.submission_count
                ):
                    raise ValueError(
                        "Related rows changed after preview. Run the command "
                        "again to review updated counts."
                    )
                if not current.event_ids:
                    raise ValueError("No events were found in the last 12 weeks.")

                await cur.execute(
                    """
                    SELECT id, event_date, game_id, format_id, last_update,
                           event_type_id, event_name, custom_event_id, created_at,
                           created_by, league_id, is_complete
                    FROM public.events
                    WHERE id = ANY(%s)
                    ORDER BY id
                    """,
                    (list(current.event_ids),),
                )
                source_events = await cur.fetchall()

                copied_pairings = 0
                copied_submissions = 0
                for event in source_events:
                    (
                        old_event_id,
                        event_date,
                        game_id,
                        format_id,
                        last_update,
                        event_type_id,
                        event_name,
                        custom_event_id,
                        created_at,
                        created_by,
                        league_id,
                        is_complete,
                    ) = event

                    await cur.execute(
                        """
                        INSERT INTO public.events (
                            discord_id, event_date, game_id, format_id, last_update,
                            event_type_id, event_name, custom_event_id, created_at,
                            created_by, league_id, is_complete
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            target_discord_id,
                            event_date,
                            game_id,
                            format_id,
                            last_update,
                            event_type_id,
                            event_name,
                            custom_event_id,
                            created_at,
                            created_by,
                            league_id,
                            is_complete,
                        ),
                    )
                    new_event_id = (await cur.fetchone())[0]

                    await cur.execute(
                        """
                        INSERT INTO public.pairings (
                            event_id, round_number, submitter_id, player1_name,
                            player1_game_wins, player2_name, player2_game_wins
                        )
                        SELECT %s, round_number, submitter_id, player1_name,
                               player1_game_wins, player2_name, player2_game_wins
                        FROM public.pairings
                        WHERE event_id = %s
                        """,
                        (new_event_id, old_event_id),
                    )
                    copied_pairings += cur.rowcount

                    await cur.execute(
                        """
                        INSERT INTO public.archetype_submissions (
                            event_id, player_name, archetype_played, date_submitted,
                            submitter_id, submitter_username, submitter_discord_id,
                            submitter_discord_name, reported, is_submitter
                        )
                        SELECT %s, player_name, archetype_played, date_submitted,
                               submitter_id, submitter_username,
                               submitter_discord_id, submitter_discord_name,
                               reported, is_submitter
                        FROM public.archetype_submissions
                        WHERE event_id = %s
                        """,
                        (new_event_id, old_event_id),
                    )
                    copied_submissions += cur.rowcount

                if len(source_events) != current.event_count:
                    raise RuntimeError(
                        "The source event count changed during the copy."
                    )
                if (
                    copied_pairings != current.pairing_count
                    or copied_submissions != current.submission_count
                ):
                    raise RuntimeError(
                        "Related row counts changed during the copy."
                    )

                return RecentEventCopyResult(
                    event_count=len(source_events),
                    pairing_count=copied_pairings,
                    submission_count=copied_submissions,
                )
