import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from api_calls import moxfield_decklist
from custom_errors import KnownError


class MoxfieldDeckIdTests(unittest.TestCase):
    def test_extracts_id_from_www_url_with_query_and_trailing_slash(self):
        deck_id = moxfield_decklist.GetMoxfieldDeckId(
            "https://www.moxfield.com/decks/abc_123-X/?utm_source=test"
        )

        self.assertEqual(deck_id, "abc_123-X")

    def test_rejects_non_moxfield_urls(self):
        with self.assertRaises(KnownError):
            moxfield_decklist.GetMoxfieldDeckId(
                "https://example.com/decks/abc123"
            )


class GetMoxfieldArchetypeTests(unittest.IsolatedAsyncioTestCase):
    async def test_saves_canonical_deck_url_with_imported_deck(self):
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"mainboard": {}, "sideboard": {}},
        )
        with (
            patch.object(moxfield_decklist.requests, "get", return_value=response),
            patch.object(
                moxfield_decklist, "AddDeck", new=AsyncMock(return_value=10)
            ) as add_deck,
            patch.object(moxfield_decklist, "AddCards", new=AsyncMock()),
            patch.object(
                moxfield_decklist,
                "SelectArchetype",
                new=AsyncMock(return_value="Control"),
            ),
        ):
            result = await moxfield_decklist.GetMoxfieldArchetype(
                "https://www.moxfield.com/decks/abc123?source=discord",
                SimpleNamespace(id=5),
                SimpleNamespace(format_name="Standard"),
                "Player One",
            )

        self.assertEqual(result, "Control")
        add_deck.assert_awaited_once_with(
            "Player One", 5, "https://moxfield.com/decks/abc123"
        )


if __name__ == "__main__":
    unittest.main()
