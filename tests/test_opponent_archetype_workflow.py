import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from data.archetype_data import OpponentArchetype
from input_modals.opponent_archetype_modal import OpponentArchetypeModal
from services import opponent_archetype_workflow as workflow
from tuple_conversions import PlayerArchetype


def make_interaction():
    return SimpleNamespace(
        response=SimpleNamespace(
            send_modal=AsyncMock(),
            defer=AsyncMock(),
        ),
        followup=SimpleNamespace(send=AsyncMock()),
        user=SimpleNamespace(id=123, name="Submitter"),
        guild_id=456,
        guild=SimpleNamespace(name="Example Server"),
    )


class OpponentArchetypeWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def test_modal_lists_rounds_and_defaults_existing_archetypes(self):
        modal = OpponentArchetypeModal(
            [OpponentArchetype(3, "Opponent", "Existing Deck")]
        )

        self.assertEqual(modal.children[0].text, "Round 3 - Opponent")
        self.assertEqual(modal.children[0].component.default, "Existing Deck")

    async def test_modal_only_collects_nonblank_changed_values(self):
        modal = SimpleNamespace(
            opponents=[
                OpponentArchetype(1, "Unchanged", "Existing Deck"),
                OpponentArchetype(2, "Changed", None),
                OpponentArchetype(3, "Cleared", "Existing Deck"),
            ],
            children=[
                SimpleNamespace(component=SimpleNamespace(value="Existing Deck")),
                SimpleNamespace(component=SimpleNamespace(value="new deck")),
                SimpleNamespace(component=SimpleNamespace(value="")),
            ],
            new_archetypes=[],
            interaction=None,
            is_submitted=False,
        )
        submit_interaction = make_interaction()

        await OpponentArchetypeModal.on_submit(modal, submit_interaction)

        self.assertEqual(
            modal.new_archetypes, [PlayerArchetype("Changed", "New Deck")]
        )
        self.assertIs(modal.interaction, submit_interaction)
        submit_interaction.response.defer.assert_awaited_once_with(ephemeral=True)

    async def test_changed_archetypes_are_saved_as_opponent_submissions(self):
        interaction = make_interaction()
        modal_interaction = make_interaction()
        modal = SimpleNamespace(
            is_submitted=True,
            interaction=modal_interaction,
            new_archetypes=[PlayerArchetype("Opponent", "Deck Name")],
            wait=AsyncMock(),
        )
        event = SimpleNamespace(id=10)

        with (
            patch.object(
                workflow, "OpponentArchetypeModal", return_value=modal
            ),
            patch.object(
                workflow, "BulkAddArchetypes", new_callable=AsyncMock
            ) as save,
        ):
            result = await workflow.SubmitOpponentArchetypeBatch(
                interaction,
                make_interaction(),
                event,
                [OpponentArchetype(1, "Opponent", None)],
            )

        self.assertIs(result, modal_interaction)
        save.assert_awaited_once_with(
            event,
            [PlayerArchetype("Opponent", "Deck Name")],
            123,
            "Submitter",
            456,
            "Example Server",
            is_submitter=False,
        )
        modal_interaction.followup.send.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
