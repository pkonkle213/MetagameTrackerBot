import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from services import one_event_decklists
from tuple_conversions import Deck


class OneEventDecklistsTests(unittest.IsolatedAsyncioTestCase):
    async def get_first_embed(self, link: str | None):
        interaction = SimpleNamespace(
            followup=SimpleNamespace(send=AsyncMock())
        )
        event = SimpleNamespace(id=7)
        deck = Deck(1, "Control", 3, 1, 0, link)

        with (
            patch.object(
                one_event_decklists, "GetDecks", new=AsyncMock(return_value=[deck])
            ),
            patch.object(
                one_event_decklists, "GetDecklists", new=AsyncMock(return_value=[])
            ),
            patch.object(one_event_decklists, "PaginationView", return_value=object()),
        ):
            await one_event_decklists.OneEventDecklists(interaction, event)

        return interaction.followup.send.await_args.kwargs["embed"]

    async def test_embed_includes_saved_deck_link(self):
        embed = await self.get_first_embed("https://moxfield.com/decks/example")

        self.assertEqual(embed.fields[0].name, "Deck link")
        self.assertEqual(embed.fields[0].value, "https://moxfield.com/decks/example")

    async def test_embed_shows_no_link_when_missing(self):
        embed = await self.get_first_embed(None)

        self.assertEqual(embed.fields[0].name, "Deck link")
        self.assertEqual(embed.fields[0].value, "No link")


if __name__ == "__main__":
    unittest.main()
