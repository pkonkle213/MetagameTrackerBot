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

    async def test_blank_batch_reports_no_changes_and_recurses(self):
        players = [PlayerArchetype(f"Player {i}", "") for i in range(6)]
        active_interaction = make_interaction()
        modal_instances = []
        confirmation_instances = []

        def make_modal(batch):
            modal = SimpleNamespace(
                players=batch,
                new_archetypes=(
                    [PlayerArchetype("Player 5", "Deck")] if len(batch) == 1 else []
                ),
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
        submitted_archetypes = []
        event = object()
        with (
            patch.object(workflow, "MassArchetypeSubmit", side_effect=make_modal),
            patch.object(workflow, "ConfirmEvent", side_effect=make_confirmation),
            patch.object(
                workflow, "BuildTableOutput", return_value=["table"]
            ) as build_table,
            patch.object(workflow, "BulkAddArchetypes", new_callable=AsyncMock) as save,
        ):
            returned_interaction = await workflow.SubmitArchetypeBatch(
                original_interaction,
                active_interaction,
                event,
                players,
                submitted_archetypes,
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
        self.assertEqual(save.await_count, 1)
        self.assertEqual(
            submitted_archetypes, [PlayerArchetype("Player 5", "Deck")]
        )
        self.assertTrue(original_interaction.followup.send.await_args_list)
        self.assertTrue(
            all(
                call.kwargs.get("ephemeral") is True
                for call in original_interaction.followup.send.await_args_list
            )
        )
        build_table.assert_called_once()
        table_messages = [
            call
            for call in original_interaction.followup.send.await_args_list
            if call.args == ("table",)
        ]
        self.assertEqual(len(table_messages), 1)
        self.assertTrue(table_messages[0].kwargs["ephemeral"])
        self.assertTrue(
            any(
                "No archetype changes were made in this batch" in call.args[0]
                for call in original_interaction.followup.send.await_args_list
            )
        )

    async def test_final_blank_batch_is_not_saved(self):
        active_interaction = make_interaction()
        modal = SimpleNamespace(
            players=[PlayerArchetype(f"Player {i}", "") for i in range(5)],
            new_archetypes=[],
            is_submitted=True,
            interaction=make_interaction(),
            wait=AsyncMock(),
        )
        confirmation = SimpleNamespace(
            action=ViewButtonEnum.Continue.value,
            interaction=make_interaction(),
            wait=AsyncMock(),
        )
        event = object()
        submitted_archetypes = []

        with (
            patch.object(workflow, "MassArchetypeSubmit", return_value=modal),
            patch.object(workflow, "ConfirmEvent", return_value=confirmation),
            patch.object(workflow, "BuildTableOutput") as build_table,
            patch.object(workflow, "BulkAddArchetypes", new_callable=AsyncMock) as save,
        ):
            returned_interaction = await workflow.SubmitArchetypeBatch(
                make_interaction(),
                active_interaction,
                event,
                modal.players,
                submitted_archetypes,
            )

        self.assertIs(returned_interaction, confirmation.interaction)
        build_table.assert_not_called()
        save.assert_not_awaited()
        self.assertEqual(submitted_archetypes, [])

    async def test_command_notifies_once_after_all_batches(self):
        bot = object()
        interaction = make_interaction()
        store, game, format = object(), object(), object()
        event = SimpleNamespace(id=10)
        active_interaction = make_interaction()
        returned_interaction = make_interaction()
        players = [PlayerArchetype("Player One", ""), PlayerArchetype("Player Two", "")]
        submitted = [
            PlayerArchetype("Player One", "Deck One"),
            PlayerArchetype("Player Two", "Deck Two"),
        ]

        async def submit_batches(
            command_interaction,
            selected_interaction,
            selected_event,
            batch_players,
            submitted_archetypes,
        ):
            submitted_archetypes.extend(submitted)
            return returned_interaction

        with (
            patch.object(
                workflow,
                "SelectEvent",
                new=AsyncMock(return_value=(event, active_interaction)),
            ),
            patch.object(
                workflow, "GetPlayersInEvent", new=AsyncMock(return_value=players)
            ),
            patch.object(
                workflow,
                "SubmitArchetypeBatch",
                new=AsyncMock(side_effect=submit_batches),
            ),
            patch.object(
                workflow,
                "NotifyArchetypeSubmission",
                new=AsyncMock(return_value=event),
            ) as notify,
        ):
            await workflow.SubmitMassArchetypes(
                bot, interaction, store, game, format
            )

        notify.assert_awaited_once_with(bot, interaction, event, submitted, store, "")


if __name__ == "__main__":
    unittest.main()
