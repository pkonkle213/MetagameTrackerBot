import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from input_modals.mass_archetype_modal import MassArchetypeSubmit
from services import mass_archetype_workflow as workflow
from tuple_conversions import PlayerArchetype, ViewButtonEnum


def make_interaction():
    return SimpleNamespace(
        response=SimpleNamespace(
            send_modal=AsyncMock(),
            defer=AsyncMock(),
        ),
        followup=SimpleNamespace(send=AsyncMock()),
        user=SimpleNamespace(id=1, name="submitter"),
        guild_id=2,
        guild=SimpleNamespace(name="test guild"),
    )


class MassArchetypeWorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_modal_stores_and_acknowledges_its_submit_interaction(self):
        modal = SimpleNamespace(
            players=[PlayerArchetype("Player", "")],
            children=[SimpleNamespace(component=SimpleNamespace(value="Deck"))],
            new_archetypes=[],
            interaction=None,
            is_submitted=False,
        )
        submitted_interaction = make_interaction()

        await MassArchetypeSubmit.on_submit(modal, submitted_interaction)

        self.assertIs(modal.interaction, submitted_interaction)
        self.assertEqual(
            modal.new_archetypes, [PlayerArchetype("Player", "Deck")]
        )
        submitted_interaction.response.defer.assert_awaited_once_with(ephemeral=True)

    async def test_batches_recurse_using_each_confirmation_interaction(self):
        players = [PlayerArchetype(f"Player {i}", "") for i in range(6)]
        active_interaction = make_interaction()
        modal_instances = []
        confirmation_instances = []

        def make_modal(batch):
            modal = SimpleNamespace(
                players=batch,
                new_archetypes=[],
                is_submitted=True,
                interaction=make_interaction(),
                wait=AsyncMock(),
            )
            modal_instances.append(modal)
            return modal

        def make_confirmation():
            confirmation = SimpleNamespace(
                action=ViewButtonEnum.Continue.value,
                interaction=make_interaction(),
                wait=AsyncMock(),
            )
            confirmation_instances.append(confirmation)
            return confirmation

        original_interaction = make_interaction()
        with (
            patch.object(workflow, "MassArchetypeSubmit", side_effect=make_modal),
            patch.object(workflow, "ConfirmEvent", side_effect=make_confirmation),
            patch.object(workflow, "BuildTableOutput", return_value=["table"]),
            patch.object(workflow, "BulkAddArchetypes", new_callable=AsyncMock) as save,
        ):
            returned_interaction = await workflow.SubmitArchetypeBatch(
                original_interaction,
                active_interaction,
                object(),
                players,
            )

        self.assertEqual([len(modal.players) for modal in modal_instances], [5, 1])
        active_interaction.response.send_modal.assert_awaited_once_with(
            modal_instances[0]
        )
        confirmation_instances[0].interaction.response.send_modal.assert_awaited_once_with(
            modal_instances[1]
        )
        confirmation_instances[1].interaction.response.defer.assert_awaited_once_with(
            ephemeral=True
        )
        self.assertIs(returned_interaction, confirmation_instances[1].interaction)
        self.assertEqual(save.await_count, 2)


if __name__ == "__main__":
    unittest.main()
