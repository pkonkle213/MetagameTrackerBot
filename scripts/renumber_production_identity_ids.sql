-- One-time production data operation: densely renumber every public identity
-- column named "id", remap its foreign-key references, and restart its identity
-- sequence. No rows are deleted; every non-ID field is left unchanged.
--
-- Run only in the Production SQL console, after:
--   1. Confirming production point-in-time recovery is enabled.
--   2. Stopping the bot and other writers for the duration of this transaction.
--   3. Confirming that changing existing IDs will not break external references.
--
-- This takes ACCESS EXCLUSIVE locks on affected tables and intentionally fails
-- rather than proceeding if it finds an unsupported or ambiguous relationship.
-- Review the mappings and expected effects before running. Do not run in dev.

BEGIN;
SET LOCAL lock_timeout = '10s';
SET LOCAL statement_timeout = '5min';

CREATE TEMP TABLE _renumber_identity_tables (
    relid oid PRIMARY KEY,
    schema_name text NOT NULL,
    table_name text NOT NULL,
    id_type oid NOT NULL
) ON COMMIT DROP;

INSERT INTO _renumber_identity_tables (relid, schema_name, table_name, id_type)
SELECT c.oid, n.nspname, c.relname, a.atttypid
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_attribute a ON a.attrelid = c.oid
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p')
  AND a.attname = 'id'
  AND a.attidentity IN ('a', 'd')
  AND NOT a.attisdropped;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_temp._renumber_identity_tables) THEN
        RAISE EXCEPTION 'No public identity columns named id were found';
    END IF;
END
$$;

CREATE TEMP TABLE _renumber_fk_columns ON COMMIT DROP AS
SELECT
    c.oid AS constraint_oid,
    c.confrelid AS referenced_relid,
    src_ns.nspname AS referencing_schema,
    src.relname AS referencing_table,
    src_att.attname AS referencing_column,
    ref.relname AS referenced_table
FROM pg_constraint c
JOIN pg_class src ON src.oid = c.conrelid
JOIN pg_namespace src_ns ON src_ns.oid = src.relnamespace
JOIN LATERAL unnest(c.conkey) WITH ORDINALITY AS src_key(attnum, ord) ON true
JOIN LATERAL unnest(c.confkey) WITH ORDINALITY AS ref_key(attnum, ord)
    ON ref_key.ord = src_key.ord
JOIN pg_attribute src_att
    ON src_att.attrelid = src.oid AND src_att.attnum = src_key.attnum
JOIN pg_class ref ON ref.oid = c.confrelid
JOIN pg_attribute ref_att
    ON ref_att.attrelid = ref.oid AND ref_att.attnum = ref_key.attnum
JOIN pg_temp._renumber_identity_tables identity_table
    ON identity_table.relid = ref.oid
WHERE c.contype = 'f'
  AND ref_att.attname = 'id';

CREATE TEMP TABLE _renumber_fk_state ON COMMIT DROP AS
SELECT DISTINCT
    c.conrelid AS relid,
    src_ns.nspname AS schema_name,
    src.relname AS table_name,
    c.conname AS constraint_name,
    c.condeferrable AS was_deferrable,
    c.condeferred AS was_initially_deferred
FROM pg_constraint c
JOIN pg_class src ON src.oid = c.conrelid
JOIN pg_namespace src_ns ON src_ns.oid = src.relnamespace
JOIN pg_temp._renumber_fk_columns fk ON fk.constraint_oid = c.oid;

DO $$
DECLARE
    r record;
BEGIN
    -- Lock tables in a stable order so writers cannot change rows between the
    -- mapping and update phases.
    FOR r IN
        SELECT schema_name, table_name
        FROM (
            SELECT schema_name, table_name
            FROM pg_temp._renumber_identity_tables
            UNION
            SELECT referencing_schema, referencing_table
            FROM pg_temp._renumber_fk_columns
        ) AS affected
        ORDER BY schema_name, table_name
    LOOP
        EXECUTE format(
            'LOCK TABLE %I.%I IN ACCESS EXCLUSIVE MODE',
            r.schema_name, r.table_name
        );
    END LOOP;

    -- A single column cannot safely refer to two different ID domains.
    IF EXISTS (
        SELECT 1
        FROM pg_temp._renumber_fk_columns
        GROUP BY referencing_schema, referencing_table, referencing_column
        HAVING count(DISTINCT referenced_relid) > 1
    ) THEN
        RAISE EXCEPTION
            'An FK column references multiple identity tables; refusing ambiguous remapping';
    END IF;
END
$$;

CREATE TEMP TABLE _renumber_id_map (
    table_name text NOT NULL,
    old_id bigint NOT NULL,
    temporary_id bigint NOT NULL,
    new_id bigint NOT NULL,
    PRIMARY KEY (table_name, old_id),
    UNIQUE (table_name, temporary_id),
    UNIQUE (table_name, new_id)
) ON COMMIT DROP;

DO $$
DECLARE
    t record;
BEGIN
    FOR t IN
        SELECT schema_name, table_name
        FROM pg_temp._renumber_identity_tables
        ORDER BY schema_name, table_name
    LOOP
        EXECUTE format(
            'INSERT INTO pg_temp._renumber_id_map '
            '(table_name, old_id, temporary_id, new_id) '
            'SELECT %L, id::bigint, '
            '((max(id) OVER ())::bigint + row_number() OVER (ORDER BY id))::bigint, '
            'row_number() OVER (ORDER BY id)::bigint '
            'FROM %I.%I',
            t.table_name, t.schema_name, t.table_name
        );
    END LOOP;
END
$$;

DO $$
DECLARE
    t record;
    row_count bigint;
    max_temporary_id bigint;
BEGIN
    -- Validate that temporary IDs and the next sequence value fit each
    -- identity column's integer type before changing any data.
    FOR t IN
        SELECT i.table_name, i.id_type, count(m.old_id) AS row_count,
               coalesce(max(m.temporary_id), 0) AS max_temporary_id
        FROM pg_temp._renumber_identity_tables i
        LEFT JOIN pg_temp._renumber_id_map m ON m.table_name = i.table_name
        GROUP BY i.table_name, i.id_type
    LOOP
        row_count := t.row_count;
        max_temporary_id := t.max_temporary_id;

        IF t.id_type = 'integer'::regtype::oid
           AND (max_temporary_id > 2147483647 OR row_count >= 2147483647) THEN
            RAISE EXCEPTION 'ID range would overflow integer in table %', t.table_name;
        ELSIF t.id_type = 'bigint'::regtype::oid
           AND (max_temporary_id = 9223372036854775807
                OR row_count = 9223372036854775807) THEN
            RAISE EXCEPTION 'ID range would overflow bigint in table %', t.table_name;
        END IF;
    END LOOP;
END
$$;

DO $$
DECLARE
    f record;
BEGIN
    -- FK checks are deferred only inside this transaction so references can
    -- move through temporary IDs without ever leaving the final DB inconsistent.
    FOR f IN
        SELECT *
        FROM pg_temp._renumber_fk_state
        WHERE NOT was_deferrable
        ORDER BY schema_name, table_name, constraint_name
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.%I ALTER CONSTRAINT %I DEFERRABLE INITIALLY DEFERRED',
            f.schema_name, f.table_name, f.constraint_name
        );
    END LOOP;
END
$$;

SET CONSTRAINTS ALL DEFERRED;

-- Move FK values to temporary IDs, then move parent IDs. This handles both
-- ON UPDATE CASCADE and NO ACTION constraints without deleting any records.
DO $$
DECLARE
    f record;
BEGIN
    FOR f IN
        SELECT * FROM pg_temp._renumber_fk_columns
        ORDER BY referencing_schema, referencing_table, referencing_column,
                 referenced_table
    LOOP
        EXECUTE format(
            'UPDATE %I.%I AS child SET %I = m.temporary_id '
            'FROM pg_temp._renumber_id_map AS m '
            'WHERE m.table_name = %L AND child.%I::bigint = m.old_id',
            f.referencing_schema, f.referencing_table, f.referencing_column,
            f.referenced_table, f.referencing_column
        );
    END LOOP;
END
$$;

DO $$
DECLARE
    t record;
BEGIN
    FOR t IN
        SELECT schema_name, table_name
        FROM pg_temp._renumber_identity_tables
        ORDER BY schema_name, table_name
    LOOP
        EXECUTE format(
            'UPDATE %I.%I AS target SET id = m.temporary_id '
            'FROM pg_temp._renumber_id_map AS m '
            'WHERE m.table_name = %L AND target.id::bigint = m.old_id',
            t.schema_name, t.table_name, t.table_name
        );
    END LOOP;
END
$$;

DO $$
DECLARE
    t record;
BEGIN
    FOR t IN
        SELECT schema_name, table_name
        FROM pg_temp._renumber_identity_tables
        ORDER BY schema_name, table_name
    LOOP
        EXECUTE format(
            'UPDATE %I.%I AS target SET id = m.new_id '
            'FROM pg_temp._renumber_id_map AS m '
            'WHERE m.table_name = %L AND target.id::bigint = m.temporary_id',
            t.schema_name, t.table_name, t.table_name
        );
    END LOOP;
END
$$;

DO $$
DECLARE
    f record;
BEGIN
    FOR f IN
        SELECT * FROM pg_temp._renumber_fk_columns
        ORDER BY referencing_schema, referencing_table, referencing_column,
                 referenced_table
    LOOP
        EXECUTE format(
            'UPDATE %I.%I AS child SET %I = m.new_id '
            'FROM pg_temp._renumber_id_map AS m '
            'WHERE m.table_name = %L AND child.%I::bigint = m.temporary_id',
            f.referencing_schema, f.referencing_table, f.referencing_column,
            f.referenced_table, f.referencing_column
        );
    END LOOP;
END
$$;

DO $$
DECLARE
    t record;
    actual_count bigint;
    actual_min bigint;
    actual_max bigint;
    expected_count bigint;
    next_id bigint;
BEGIN
    FOR t IN
        SELECT schema_name, table_name
        FROM pg_temp._renumber_identity_tables
        ORDER BY schema_name, table_name
    LOOP
        EXECUTE format(
            'SELECT count(*), min(id)::bigint, max(id)::bigint FROM %I.%I',
            t.schema_name, t.table_name
        ) INTO actual_count, actual_min, actual_max;

        SELECT count(*) INTO expected_count
        FROM pg_temp._renumber_id_map
        WHERE table_name = t.table_name;

        IF actual_count <> expected_count
           OR (actual_count > 0 AND (actual_min <> 1 OR actual_max <> actual_count)) THEN
            RAISE EXCEPTION
                'Dense ID verification failed for %.%: rows %, min %, max %',
                t.schema_name, t.table_name, actual_count, actual_min, actual_max;
        END IF;

        next_id := actual_count + 1;
        EXECUTE format(
            'ALTER TABLE %I.%I ALTER COLUMN id RESTART WITH %s',
            t.schema_name, t.table_name, next_id
        );
    END LOOP;
END
$$;

-- Validate all deferred foreign keys before restoring their original settings.
SET CONSTRAINTS ALL IMMEDIATE;

DO $$
DECLARE
    f record;
BEGIN
    FOR f IN
        SELECT *
        FROM pg_temp._renumber_fk_state
        ORDER BY schema_name, table_name, constraint_name
    LOOP
        IF NOT f.was_deferrable THEN
            EXECUTE format(
                'ALTER TABLE %I.%I ALTER CONSTRAINT %I NOT DEFERRABLE',
                f.schema_name, f.table_name, f.constraint_name
            );
        ELSIF f.was_initially_deferred THEN
            EXECUTE format(
                'ALTER TABLE %I.%I ALTER CONSTRAINT %I DEFERRABLE INITIALLY DEFERRED',
                f.schema_name, f.table_name, f.constraint_name
            );
        ELSE
            EXECUTE format(
                'ALTER TABLE %I.%I ALTER CONSTRAINT %I DEFERRABLE INITIALLY IMMEDIATE',
                f.schema_name, f.table_name, f.constraint_name
            );
        END IF;
    END LOOP;
END
$$;

COMMIT;

-- Post-commit verification: each non-empty identity table should have IDs
-- 1..row_count. The sequence restart values are row_count + 1.
SELECT 'archetype_submissions' AS table_name, count(*) AS row_count, min(id) AS min_id, max(id) AS max_id FROM public.archetype_submissions
UNION ALL SELECT 'banned_words', count(*), min(id), max(id) FROM public.banned_words
UNION ALL SELECT 'command_invocations', count(*), min(id), max(id) FROM public.command_invocations
UNION ALL SELECT 'commands', count(*), min(id), max(id) FROM public.commands
UNION ALL SELECT 'decklists', count(*), min(id), max(id) FROM public.decklists
UNION ALL SELECT 'decks', count(*), min(id), max(id) FROM public.decks
UNION ALL SELECT 'event_types', count(*), min(id), max(id) FROM public.event_types
UNION ALL SELECT 'events', count(*), min(id), max(id) FROM public.events
UNION ALL SELECT 'formats', count(*), min(id), max(id) FROM public.formats
UNION ALL SELECT 'games', count(*), min(id), max(id) FROM public.games
UNION ALL SELECT 'hub_league_stores', count(*), min(id), max(id) FROM public.hub_league_stores
UNION ALL SELECT 'leagues', count(*), min(id), max(id) FROM public.leagues
UNION ALL SELECT 'payments', count(*), min(id), max(id) FROM public.payments
UNION ALL SELECT 'regions', count(*), min(id), max(id) FROM public.regions
UNION ALL SELECT 'stores_approved_hubs', count(*), min(id), max(id) FROM public.stores_approved_hubs
ORDER BY table_name;
