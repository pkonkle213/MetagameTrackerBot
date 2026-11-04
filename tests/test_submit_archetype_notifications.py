import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from services import submit_archetype_service as service
from tuple_conversions import Event, PlayerArchetype


class CheckEventPercentageTests(unittest.IsolatedAsyncioTestCase):
    async def test_catches_up_all_milestones_reached_by_a_batch(self):
        event = Event(
            1,
            None,
            None,
            2,
            date(2026, 11, 4),
            1,
            1,
            0,
            1,
            "Weekly Event",
            1,
            5,
            None,
            False,
        )

        with (
            patch.object(
                service,
                "GetEventReportedPercentage",
                new=AsyncMock(return_value=0.76),
            ),
            patch.object(service, "UpdateEvent", new=AsyncMock()) as update,
        ):
            public_output, full_event, updates_counted = (
                await service.CheckEventPercentage(event)
            )

        self.assertEqual(updates_counted, 3)
        self.assertEqual(update.await_count, 3)
        self.assertIn("76% reported", public_output)
        self.assertIsNone(full_event)

    def test_build_message_includes_every_submitted_archetype(self):
        interaction = SimpleNamespace(
            user=SimpleNamespace(display_name="Submitter", id=123),
            guild=SimpleNamespace(name="Example Server", id=456),
        )
        event = SimpleNamespace(event_name="Weekly Event")
        archetypes = [
            PlayerArchetype("Player One", "Deck One"),
            PlayerArchetype("Player Two", "Deck Two"),
        ]

        message = service.BuildMessage(interaction, event, archetypes)

        self.assertIn("Archetype submitted: Deck One", message)
        self.assertIn("For player name: Player One", message)
        self.assertIn("Archetype submitted: Deck Two", message)
        self.assertIn("For player name: Player Two", message)


if __name__ == "__main__":
    unittest.main()
