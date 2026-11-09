import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from data.submitted_archetypes_data import GetSubmittedArchetypes


class FakeCursor:
    def __init__(self):
        self.command = None
        self.parameters = None
        self.rows = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def execute(self, command, parameters):
        self.command = command
        self.parameters = parameters

    async def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()

    def cursor(self):
        return self.fake_cursor

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class GetSubmittedArchetypesTests(unittest.IsolatedAsyncioTestCase):
    async def test_uses_schema_column_and_parameterized_optional_filters(self):
        connection = FakeConnection()
        expected_rows = [("event row",)]
        connection.fake_cursor.rows = expected_rows

        with patch(
            "data.submitted_archetypes_data.AsyncConnection.connect",
            new=AsyncMock(return_value=connection),
        ):
            rows = await GetSubmittedArchetypes(
                game=SimpleNamespace(id=11),
                format=SimpleNamespace(id=22),
                store=SimpleNamespace(discord_id=33),
                player_name="D'Angelo",
                date_used=date(2026, 11, 9),
            )

        self.assertEqual(rows, expected_rows)
        self.assertIn("ua.asu_submitter_id", connection.fake_cursor.command)
        self.assertIn("e.format_id = %s", connection.fake_cursor.command)
        self.assertIn("e.event_date = %s", connection.fake_cursor.command)
        self.assertIn("UPPER(ua.player_name) = UPPER(%s)", connection.fake_cursor.command)
        self.assertEqual(
            connection.fake_cursor.parameters,
            [33, 11, 22, date(2026, 11, 9), "D'Angelo"],
        )

    async def test_includes_format_without_date_or_player_filters(self):
        connection = FakeConnection()

        with patch(
            "data.submitted_archetypes_data.AsyncConnection.connect",
            new=AsyncMock(return_value=connection),
        ):
            await GetSubmittedArchetypes(
                game=SimpleNamespace(id=11),
                format=None,
                store=SimpleNamespace(discord_id=33),
                player_name="",
                date_used=None,
            )

        self.assertIn("f.format_name", connection.fake_cursor.command)
        self.assertNotIn("e.event_date =", connection.fake_cursor.command)
        self.assertNotIn("UPPER(ua.player_name)", connection.fake_cursor.command)
        self.assertEqual(connection.fake_cursor.parameters, [33, 11])


if __name__ == "__main__":
    unittest.main()
