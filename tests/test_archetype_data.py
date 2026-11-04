import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from data.archetype_data import (
    BulkAddArchetypes,
    GetOpponentArchetypes,
    OpponentArchetype,
)


class FakeCursor:
    def __init__(self):
        self.command = None
        self.parameters = None
        self.rows = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def executemany(self, command, parameters):
        self.command = command
        self.parameters = parameters

    async def execute(self, command, parameters):
        self.command = command
        self.parameters = parameters

    async def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()
        self.commit = AsyncMock()

    def cursor(self, **kwargs):
        return self.fake_cursor

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class BulkAddArchetypesTests(unittest.IsolatedAsyncioTestCase):
    async def test_insert_placeholders_match_parameters_and_keep_submitter_id(self):
        connection = FakeConnection()
        archetype = SimpleNamespace(
            player_name="Player One",
            archetype_played="Example Deck",
        )

        with patch(
            "data.archetype_data.AsyncConnection.connect",
            new=AsyncMock(return_value=connection),
        ):
            inserted = await BulkAddArchetypes(
                SimpleNamespace(id=17),
                [archetype],
                user_id=123,
                user_name="Submitter",
                user_discord_id=456,
                user_discord_name="Example Server",
                is_submitter=True,
            )

        self.assertEqual(inserted, 1)
        self.assertEqual(connection.fake_cursor.command.count("%s"), 8)
        self.assertNotIn("via mass update", connection.fake_cursor.command)
        self.assertEqual(
            connection.fake_cursor.parameters,
            [
                (
                    17,
                    "Player One",
                    "Example Deck",
                    123,
                    "Submitter",
                    456,
                    "Example Server",
                    True,
                )
            ],
        )
        connection.commit.assert_awaited_once()


class GetOpponentArchetypesTests(unittest.IsolatedAsyncioTestCase):
    async def test_filters_by_event_user_and_server_in_round_order(self):
        connection = FakeConnection()
        expected = [OpponentArchetype(1, "Opponent", "Deck")]
        connection.fake_cursor.rows = expected

        with patch(
            "data.archetype_data.AsyncConnection.connect",
            new=AsyncMock(return_value=connection),
        ):
            result = await GetOpponentArchetypes(
                event_id=17, user_id=123, discord_id=456
            )

        self.assertEqual(result, expected)
        self.assertEqual(connection.fake_cursor.parameters, [17, 123, 456])
        self.assertIn("pn.submitter_id = %s", connection.fake_cursor.command)
        self.assertIn("e.discord_id = %s", connection.fake_cursor.command)
        self.assertIn("ORDER BY\n            fp.round_number", connection.fake_cursor.command)


if __name__ == "__main__":
    unittest.main()
