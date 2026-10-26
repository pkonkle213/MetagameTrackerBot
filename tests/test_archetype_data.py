import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from data.archetype_data import BulkAddArchetypes


class FakeCursor:
    def __init__(self):
        self.command = None
        self.parameters = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def executemany(self, command, parameters):
        self.command = command
        self.parameters = parameters


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()
        self.commit = AsyncMock()

    def cursor(self):
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


if __name__ == "__main__":
    unittest.main()
