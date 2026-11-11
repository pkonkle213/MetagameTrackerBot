import unittest
from datetime import date
from unittest.mock import AsyncMock, patch

from data import recent_event_copy_data


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.command = None
        self.parameters = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def execute(self, command, parameters):
        self.command = command
        self.parameters = parameters

    async def fetchone(self):
        return self.row

    async def fetchall(self):
        return []


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    def cursor(self):
        return self.fake_cursor


class FakeTransaction:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, *_args):
        self.connection.rolled_back = exc_type is not None


class CopyCursor(FakeCursor):
    def __init__(self, preview_row, source_event):
        super().__init__(preview_row)
        self.source_event = source_event
        self.commands = []
        self.pending_row = None
        self.pending_rows = []
        self.rowcount = 0

    async def execute(self, command, parameters=None):
        self.commands.append((command, parameters))
        self.rowcount = 0
        if "WITH candidate_events AS MATERIALIZED" in command:
            self.pending_row = self.row
        elif "SELECT id, event_date, game_id" in command:
            self.pending_rows = [self.source_event]
        elif "RETURNING id" in command:
            self.pending_row = (501,)
        elif "INSERT INTO public.pairings" in command:
            self.rowcount = 2
        elif "INSERT INTO public.archetype_submissions" in command:
            self.rowcount = 1

    async def fetchone(self):
        return self.pending_row

    async def fetchall(self):
        return self.pending_rows


class CopyConnection(FakeConnection):
    def __init__(self, cursor):
        super().__init__(cursor)
        self.rolled_back = None

    def transaction(self):
        return FakeTransaction(self)


class RecentEventCopyDataTests(unittest.IsolatedAsyncioTestCase):
    def make_preview_row(self, event_ids):
        return (
            event_ids,
            len(event_ids),
            2,
            1,
            date(2026, 8, 21),
            date(2026, 11, 10),
            True,
            True,
            "Demo Store",
            0,
        )

    async def test_preview_uses_exact_target_id_and_12_week_window(self):
        target_id = 1515166332667301968
        row = (
            [11, 12],
            2,
            3,
            4,
            date(2026, 8, 21),
            date(2026, 11, 10),
            True,
            True,
            "Demo Store",
            0,
        )
        cursor = FakeCursor(row)
        connection = FakeConnection(cursor)

        with patch.object(
            recent_event_copy_data.AsyncConnection,
            "connect",
            new_callable=AsyncMock,
            return_value=connection,
        ):
            preview = await recent_event_copy_data.PreviewRecentEventCopy(target_id)

        self.assertEqual(preview.target_discord_id, target_id)
        self.assertEqual(preview.event_ids, (11, 12))
        self.assertEqual(preview.event_count, 2)
        self.assertEqual(preview.pairing_count, 3)
        self.assertEqual(preview.submission_count, 4)
        self.assertIn("CURRENT_DATE - (%s * 7)", cursor.command)
        self.assertEqual(
            cursor.parameters,
            (12, target_id, target_id, target_id, target_id, target_id, 12),
        )

    async def test_copy_runs_in_one_transaction_and_copies_related_rows(self):
        target_id = 1515166332667301968
        event_ids = [11]
        source_event = (
            11,
            date(2026, 10, 1),
            1,
            2,
            0,
            3,
            "Weekly Event",
            None,
            None,
            target_id,
            None,
            True,
        )
        cursor = CopyCursor(self.make_preview_row(event_ids), source_event)
        connection = CopyConnection(cursor)
        preview = recent_event_copy_data.RecentEventCopyPreview(
            target_discord_id=target_id,
            event_ids=(11,),
            event_count=1,
            pairing_count=2,
            submission_count=1,
            first_event_date=date(2026, 8, 21),
            last_event_date=date(2026, 11, 10),
            target_is_store=True,
            target_is_registered=True,
            target_store_name="Demo Store",
            existing_target_event_count=0,
        )

        with patch.object(
            recent_event_copy_data.AsyncConnection,
            "connect",
            new_callable=AsyncMock,
            return_value=connection,
        ):
            result = await recent_event_copy_data.CopyRecentEventsToStore(preview)

        self.assertEqual(
            result,
            recent_event_copy_data.RecentEventCopyResult(1, 2, 1),
        )
        self.assertFalse(connection.rolled_back)
        commands = "\n".join(command for command, _ in cursor.commands)
        self.assertIn("LOCK TABLE public.archetype_submissions", commands)
        self.assertIn("INSERT INTO public.events", commands)
        self.assertIn("INSERT INTO public.pairings", commands)
        self.assertIn("INSERT INTO public.archetype_submissions", commands)

    async def test_copy_rolls_back_if_preview_is_stale(self):
        target_id = 1515166332667301968
        cursor = CopyCursor(self.make_preview_row([]), None)
        connection = CopyConnection(cursor)
        preview = recent_event_copy_data.RecentEventCopyPreview(
            target_discord_id=target_id,
            event_ids=(11,),
            event_count=1,
            pairing_count=2,
            submission_count=1,
            first_event_date=date(2026, 8, 21),
            last_event_date=date(2026, 11, 10),
            target_is_store=True,
            target_is_registered=True,
            target_store_name="Demo Store",
            existing_target_event_count=0,
        )

        with patch.object(
            recent_event_copy_data.AsyncConnection,
            "connect",
            new_callable=AsyncMock,
            return_value=connection,
        ):
            with self.assertRaisesRegex(ValueError, "source events changed"):
                await recent_event_copy_data.CopyRecentEventsToStore(preview)

        self.assertTrue(connection.rolled_back)


if __name__ == "__main__":
    unittest.main()
