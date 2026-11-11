-- One-time production copy, based on the production snapshot checked on
-- 2026-11-11:
--   Source window: event_date 2026-08-19 through 2026-11-11, inclusive
--   Destination discord_id: 1515166332667301968
--   Expected: 45 events, 815 pairings, 532 archetype_submissions
--
-- Only events, pairings, and archetype_submissions are copied. Generated event
-- and submission IDs are assigned by their identity columns; pairings use the
-- new event IDs. Other event-related tables (such as decks and standings) are
-- intentionally not copied.
--
-- Run only in the Production SQL console. Stop the bot and other writers first.
-- The transaction locks all three tables and aborts if the inspected row counts
-- or destination preconditions have changed. Do not run this script twice.

BEGIN ISOLATION LEVEL SERIALIZABLE;
SET LOCAL lock_timeout = '10s';
SET LOCAL statement_timeout = '5min';

LOCK TABLE public.archetype_submissions,
           public.events,
           public.pairings
    IN ACCESS EXCLUSIVE MODE;

CREATE TEMP TABLE _copy_source_events (
    old_event_id integer PRIMARY KEY
) ON COMMIT DROP;

CREATE TEMP TABLE _copy_event_id_map (
    old_event_id integer PRIMARY KEY,
    new_event_id integer NOT NULL UNIQUE
) ON COMMIT DROP;

INSERT INTO _copy_source_events (old_event_id)
SELECT id
FROM public.events
WHERE event_date >= DATE '2026-08-19'
  AND event_date <= DATE '2026-11-11'
  AND discord_id IS DISTINCT FROM 1515166332667301968
ORDER BY id;

DO $$
DECLARE
    target_discord_id CONSTANT bigint := 1515166332667301968;
    event_count bigint;
    pairing_count bigint;
    submission_count bigint;
    new_event_id integer;
    source_event record;
    copied_events bigint := 0;
    copied_pairings bigint;
    copied_submissions bigint;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM public.discords
        WHERE discord_id = target_discord_id
    ) OR NOT EXISTS (
        SELECT 1 FROM public.stores
        WHERE discord_id = target_discord_id
    ) THEN
        RAISE EXCEPTION
            'Destination % must exist in both discords and stores',
            target_discord_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM public.events
        WHERE discord_id = target_discord_id
          AND event_date >= DATE '2026-08-19'
          AND event_date <= DATE '2026-11-11'
    ) THEN
        RAISE EXCEPTION
            'Destination already has events in the copy window; refusing to duplicate twice';
    END IF;

    SELECT count(*) INTO event_count FROM _copy_source_events;
    SELECT count(*) INTO pairing_count
    FROM public.pairings p
    JOIN _copy_source_events s ON s.old_event_id = p.event_id;
    SELECT count(*) INTO submission_count
    FROM public.archetype_submissions a
    JOIN _copy_source_events s ON s.old_event_id = a.event_id;

    IF event_count <> 45 OR pairing_count <> 815 OR submission_count <> 532 THEN
        RAISE EXCEPTION
            'Source data changed since inspection: events %, pairings %, submissions %',
            event_count, pairing_count, submission_count;
    END IF;

    -- Insert each event separately so the old-to-new generated ID mapping is
    -- exact and does not depend on sequence ordering or concurrent inserts.
    FOR source_event IN
        SELECT e.event_date, e.game_id, e.format_id, e.last_update,
               e.event_type_id, e.event_name, e.custom_event_id, e.created_at,
               e.created_by, e.league_id, e.is_complete, e.id AS old_event_id
        FROM public.events e
        JOIN _copy_source_events s ON s.old_event_id = e.id
        ORDER BY e.id
    LOOP
        INSERT INTO public.events (
            discord_id, event_date, game_id, format_id, last_update,
            event_type_id, event_name, custom_event_id, created_at,
            created_by, league_id, is_complete
        )
        VALUES (
            target_discord_id, source_event.event_date, source_event.game_id,
            source_event.format_id, source_event.last_update,
            source_event.event_type_id, source_event.event_name,
            source_event.custom_event_id, source_event.created_at,
            source_event.created_by, source_event.league_id,
            source_event.is_complete
        )
        RETURNING id INTO new_event_id;

        INSERT INTO _copy_event_id_map (old_event_id, new_event_id)
        VALUES (source_event.old_event_id, new_event_id);

        copied_events := copied_events + 1;
    END LOOP;

    IF copied_events <> event_count THEN
        RAISE EXCEPTION 'Inserted % events; expected %', copied_events, event_count;
    END IF;

    INSERT INTO public.pairings (
        event_id, round_number, submitter_id, player1_name,
        player1_game_wins, player2_name, player2_game_wins
    )
    SELECT m.new_event_id, p.round_number, p.submitter_id, p.player1_name,
           p.player1_game_wins, p.player2_name, p.player2_game_wins
    FROM public.pairings p
    JOIN _copy_event_id_map m ON m.old_event_id = p.event_id;
    GET DIAGNOSTICS copied_pairings = ROW_COUNT;

    INSERT INTO public.archetype_submissions (
        event_id, player_name, archetype_played, date_submitted,
        submitter_id, submitter_username, submitter_discord_id,
        submitter_discord_name, reported, is_submitter
    )
    SELECT m.new_event_id, a.player_name, a.archetype_played, a.date_submitted,
           a.submitter_id, a.submitter_username, a.submitter_discord_id,
           a.submitter_discord_name, a.reported, a.is_submitter
    FROM public.archetype_submissions a
    JOIN _copy_event_id_map m ON m.old_event_id = a.event_id;
    GET DIAGNOSTICS copied_submissions = ROW_COUNT;

    IF copied_pairings <> pairing_count
       OR copied_submissions <> submission_count THEN
        RAISE EXCEPTION
            'Copied unexpected related rows: pairings %, submissions %',
            copied_pairings, copied_submissions;
    END IF;

    RAISE NOTICE
        'Copied % events, % pairings, and % archetype submissions to %',
        copied_events, copied_pairings, copied_submissions, target_discord_id;
END
$$;

COMMIT;

-- Post-commit check for the destination rows in the copied date window.
SELECT
    (SELECT count(*) FROM public.events
     WHERE discord_id = 1515166332667301968
       AND event_date >= DATE '2026-08-19'
       AND event_date <= DATE '2026-11-11') AS destination_events,
    (SELECT count(*) FROM public.pairings p
     JOIN public.events e ON e.id = p.event_id
     WHERE e.discord_id = 1515166332667301968
       AND e.event_date >= DATE '2026-08-19'
       AND e.event_date <= DATE '2026-11-11') AS destination_pairings,
    (SELECT count(*) FROM public.archetype_submissions a
     JOIN public.events e ON e.id = a.event_id
     WHERE e.discord_id = 1515166332667301968
       AND e.event_date >= DATE '2026-08-19'
       AND e.event_date <= DATE '2026-11-11') AS destination_submissions;
