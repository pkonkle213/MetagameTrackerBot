import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from services import submit_archetype_service as service
from tuple_conversions import PlayerArchetype


class SubmitArchetypeMoxfieldTests(unittest.IsolatedAsyncioTestCase):
    async def test_saves_imported_then_user_archetype(self):
        interaction = SimpleNamespace(
            guild=SimpleNamespace(name="Example Server"),
            channel=object(),
            guild_id=456,
            user=SimpleNamespace(id=123, name="Submitter"),
        )
        event = SimpleNamespace(event_name="Weekly Event")

        with (
            patch.object(
                service, "ValidateArchetypeSubmission", new=AsyncMock()
            ),
            patch.object(
                service,
                "Moxfield",
                new=AsyncMock(return_value=("Imported Deck", "", True)),
            ),
            patch.object(service, "BulkAddArchetypes", new=AsyncMock()) as bulk_add,
            patch.object(
                service, "NotifyArchetypeSubmission", new=AsyncMock()
            ) as notify,
        ):
            await service.SubmitArchetype(
                bot=object(),
                interaction=interaction,
                player_name="Player One",
                event=event,
                archetype="User Deck",
                store=None,
                hub=None,
                game=object(),
                format=object(),
                moxfield_link="5KcCmfk36EmNMH2KXRxnSw",
                is_submitter=True,
            )

        self.assertEqual(bulk_add.await_count, 2)
        first_archetype = bulk_add.await_args_list[0].args[1][0]
        second_archetype = bulk_add.await_args_list[1].args[1][0]
        self.assertEqual(first_archetype, PlayerArchetype("Player One", "Imported Deck"))
        self.assertEqual(second_archetype, PlayerArchetype("Player One", "User Deck"))
        self.assertEqual(
            notify.await_args.args[3],
            [
                PlayerArchetype("Player One", "Imported Deck"),
                PlayerArchetype("Player One", "User Deck"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
