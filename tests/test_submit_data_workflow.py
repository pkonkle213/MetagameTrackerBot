import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from commands.submit_commands import SubmitDataChecker
from custom_errors import KnownError
from services import submit_data_workflow as workflow
from tuple_conversions import (
    DataConverted,
    DataInputEnum,
    Event,
    Format,
    Game,
    Pairing,
    ReportedAsEnum,
    Standing,
    Store,
    ViewButtonEnum,
)
from views.confirm_data import ConfirmData


def make_event(
    *,
    event_id: int = 17,
    reported_as: int = ReportedAsEnum.Pairings.value,
) -> Event:
    return Event(
        event_id,
        None,
        None,
        1234,
        date(2026, 10, 19),
        1,
        2,
        0,
        1,
        "Weekly Tournament",
        reported_as,
        10,
        None,
        False,
    )


STORE = Store(1234, "Example Store", "Example Store", 1, "Owner", "", True, 1, True)
GAME = Game(1, "Magic")
FORMAT = Format(2, "Standard", None, False)
STANDINGS = [Standing("Player One", 3, 1, 0)]
PAIRINGS = [Pairing(1, "Player One", 2, 1, "Player Two")]


class BuildDataModalTests(unittest.TestCase):
    def test_selects_manual_csv_and_melee_modals_with_expected_paths(self):
        event = make_event()
        cases = (
            (DataInputEnum.Manual.value, workflow.SubmitManualDataModal, "ManualInput.txt"),
            (DataInputEnum.CSV.value, workflow.SubmitCSVDataModal, "CSVInput.txt"),
            (DataInputEnum.Melee.value, workflow.SubmitMeleeDataModal, "MeleeInput.txt"),
        )

        for input_type, expected_modal, filename in cases:
            with self.subTest(input_type=input_type):
                with patch.object(
                    workflow, "BuildFilePath", return_value=f"/upload/{filename}"
                ) as build_path:
                    modal = workflow.BuildDataModal(
                        input_type, event, STORE, GAME, FORMAT
                    )

                build_path.assert_called_once_with(STORE, GAME, FORMAT, filename)
                self.assertIsInstance(modal, expected_modal)
                self.assertEqual(modal.file_path, f"/upload/{filename}")
                self.assertEqual(modal.event, event)
                if input_type == DataInputEnum.Melee.value:
                    self.assertEqual(modal.store, STORE)

    def test_unknown_input_type_is_rejected(self):
        with self.assertRaisesRegex(KnownError, "Unknown input type"):
            workflow.BuildDataModal(999, make_event(), STORE, GAME, FORMAT)


class ReviewAndPersistenceTests(unittest.IsolatedAsyncioTestCase):
    def test_review_displays_standings_warning_and_hides_continue(self):
        data = DataConverted(None, STANDINGS, None, None, None)
        next_modal = object()

        with (
            patch.object(workflow, "BuildReviewOutput", return_value="standings"),
            patch.object(workflow, "BuildDataModal", return_value=next_modal),
        ):
            output, view = workflow.BuildDataReview(
                data, make_event(), DataInputEnum.Manual.value, STORE, GAME, FORMAT
            )

        self.assertIn("This is standings data", output)
        self.assertIs(view.next_modal, next_modal)
        self.assertFalse(view.btn_continue in view.children)
        self.assertTrue(view.btn_complete in view.children)

    def test_pairings_review_warns_when_replacing_standings(self):
        data = DataConverted(PAIRINGS, None, None, None, None)

        with (
            patch.object(workflow, "BuildReviewOutput", return_value="pairings"),
            patch.object(workflow, "BuildDataModal", return_value=object()),
        ):
            output, view = workflow.BuildDataReview(
                data,
                make_event(reported_as=ReportedAsEnum.Standings.value),
                DataInputEnum.CSV.value,
                STORE,
                GAME,
                FORMAT,
            )

        self.assertIn("overwrite the standings data", output)
        self.assertIn(view.btn_continue, view.children)

    async def test_save_routes_standings_and_pairings_to_their_own_persistence(self):
        standings_data = DataConverted(None, STANDINGS, None, None, None)
        pairings_data = DataConverted(PAIRINGS, None, None, None, None)
        empty_data = DataConverted(None, None, None, None, None)
        event = make_event()

        with (
            patch.object(
                workflow, "AddStandingResults", new_callable=AsyncMock
            ) as add_standings,
            patch.object(
                workflow, "AddPairingResults", new_callable=AsyncMock
            ) as add_pairings,
        ):
            await workflow.SaveDataSubmission(event, standings_data, 88)
            await workflow.SaveDataSubmission(event, pairings_data, 88)
            await workflow.SaveDataSubmission(event, empty_data, 88)

        add_standings.assert_awaited_once_with(event, STANDINGS, 88)
        add_pairings.assert_awaited_once_with(event, PAIRINGS, 88)


class ConfirmDataTests(unittest.IsolatedAsyncioTestCase):
    async def test_cancel_records_action_and_stops_view(self):
        view = ConfirmData(next_modal=object())
        interaction = Mock()

        await view.cancel_callback(interaction)

        self.assertEqual(view.action, ViewButtonEnum.Cancel.value)
        self.assertIs(view.interaction, interaction)
        self.assertTrue(view.is_finished())

    async def test_continue_opens_next_modal(self):
        next_modal = object()
        view = ConfirmData(next_modal=next_modal)
        interaction = Mock()
        interaction.response.send_modal = AsyncMock()

        await view.continue_callback(interaction)

        interaction.response.send_modal.assert_awaited_once_with(next_modal)
        self.assertEqual(view.action, ViewButtonEnum.Continue.value)
        self.assertTrue(view.is_finished())

    async def test_complete_and_incomplete_acknowledge_submission(self):
        for callback_name, expected_action in (
            ("complete_callback", ViewButtonEnum.DoneComplete.value),
            ("incomplete_callback", ViewButtonEnum.DoneIncomplete.value),
        ):
            with self.subTest(callback=callback_name):
                view = ConfirmData()
                interaction = Mock()
                interaction.response.send_message = AsyncMock()

                await getattr(view, callback_name)(interaction)

                interaction.response.send_message.assert_awaited_once_with(
                    "Thank you for submitting data!", ephemeral=True
                )
                self.assertEqual(view.action, expected_action)
                self.assertTrue(view.is_finished())


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    def make_modal(self, data):
        modal = Mock()
        modal.converted_data = data
        modal.interaction.followup.send = AsyncMock(return_value=Mock())
        modal.wait = AsyncMock(return_value=False)
        return modal

    def make_view(self, action, interaction, next_modal=None):
        view = Mock()
        view.action = action
        view.interaction = interaction
        view.next_modal = next_modal
        view.wait = AsyncMock(return_value=False)
        return view

    async def test_cancel_does_not_persist_data(self):
        modal = self.make_modal(DataConverted(None, STANDINGS, None, None, None))
        active_interaction = Mock()
        active_interaction.response.send_modal = AsyncMock()
        cancel_interaction = Mock()
        cancel_interaction.response.edit_message = AsyncMock()
        view = self.make_view(ViewButtonEnum.Cancel.value, cancel_interaction)

        with (
            patch.object(workflow, "BuildDataModal", return_value=modal),
            patch.object(workflow, "BuildDataReview", return_value=("review", view)),
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
            patch.object(
                workflow, "NotifyNewEventSubmission", new_callable=AsyncMock
            ) as notify,
        ):
            await workflow.SubmitEventDataWorkflow(
                Mock(), Mock(), STORE, GAME, FORMAT, make_event(),
                DataInputEnum.Manual.value, active_interaction, 88, True
            )

        active_interaction.response.send_modal.assert_awaited_once_with(modal)
        cancel_interaction.response.edit_message.assert_awaited_once_with(
            content="Data submission for this round canceled!", view=None
        )
        save.assert_not_awaited()
        notify.assert_not_awaited()

    async def test_continue_saves_each_review_then_completes_and_notifies_new_event(self):
        event = make_event()
        first_modal = self.make_modal(DataConverted(None, STANDINGS, None, None, None))
        second_modal = self.make_modal(DataConverted(PAIRINGS, None, None, None, None))
        initial_interaction = Mock()
        initial_interaction.response.send_modal = AsyncMock()
        continue_interaction = Mock()
        complete_interaction = Mock()
        first_view = self.make_view(
            ViewButtonEnum.Continue.value, continue_interaction, second_modal
        )
        second_view = self.make_view(
            ViewButtonEnum.DoneComplete.value, complete_interaction
        )
        bot = Mock()
        interaction = Mock()

        with (
            patch.object(workflow, "BuildDataModal", return_value=first_modal),
            patch.object(
                workflow,
                "BuildDataReview",
                side_effect=[("first review", first_view), ("second review", second_view)],
            ),
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
            patch.object(workflow, "CompleteEvent", new_callable=AsyncMock) as complete,
            patch.object(
                workflow, "NotifyNewEventSubmission", new_callable=AsyncMock
            ) as notify,
        ):
            await workflow.SubmitEventDataWorkflow(
                bot, interaction, STORE, GAME, FORMAT, event,
                DataInputEnum.Manual.value, initial_interaction, 88, True
            )

        initial_interaction.response.send_modal.assert_awaited_once_with(first_modal)
        self.assertEqual(
            [await_args.args for await_args in save.await_args_list],
            [
                (event, first_modal.converted_data, 88),
                (event, second_modal.converted_data, 88),
            ],
        )
        complete.assert_awaited_once_with(event.id)
        notify.assert_awaited_once_with(bot, interaction, STORE, event)

    async def test_incomplete_submission_saves_but_does_not_complete(self):
        event = make_event()
        modal = self.make_modal(DataConverted(PAIRINGS, None, None, None, None))
        active_interaction = Mock()
        active_interaction.response.send_modal = AsyncMock()
        done_interaction = Mock()
        view = self.make_view(ViewButtonEnum.DoneIncomplete.value, done_interaction)

        with (
            patch.object(workflow, "BuildDataModal", return_value=modal),
            patch.object(workflow, "BuildDataReview", return_value=("review", view)),
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
            patch.object(workflow, "CompleteEvent", new_callable=AsyncMock) as complete,
            patch.object(
                workflow, "NotifyNewEventSubmission", new_callable=AsyncMock
            ) as notify,
        ):
            await workflow.SubmitEventDataWorkflow(
                Mock(), Mock(), STORE, GAME, FORMAT, event,
                DataInputEnum.Melee.value, active_interaction, 88, True
            )

        save.assert_awaited_once_with(event, modal.converted_data, 88)
        complete.assert_not_awaited()
        notify.assert_awaited_once()

    async def test_existing_event_completion_does_not_send_new_event_notifications(self):
        event = make_event()
        modal = self.make_modal(DataConverted(None, STANDINGS, None, None, None))
        active_interaction = Mock()
        active_interaction.response.send_modal = AsyncMock()
        complete_interaction = Mock()
        view = self.make_view(
            ViewButtonEnum.DoneComplete.value, complete_interaction
        )

        with (
            patch.object(workflow, "BuildDataModal", return_value=modal),
            patch.object(workflow, "BuildDataReview", return_value=("review", view)),
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
            patch.object(workflow, "CompleteEvent", new_callable=AsyncMock) as complete,
            patch.object(
                workflow, "NotifyNewEventSubmission", new_callable=AsyncMock
            ) as notify,
        ):
            await workflow.SubmitEventDataWorkflow(
                Mock(), Mock(), STORE, GAME, FORMAT, event,
                DataInputEnum.Manual.value, active_interaction, 88, False
            )

        save.assert_awaited_once_with(event, modal.converted_data, 88)
        complete.assert_awaited_once_with(event.id)
        notify.assert_not_awaited()

    async def test_modal_timeout_reports_no_data_added(self):
        modal = self.make_modal(DataConverted(None, STANDINGS, None, None, None))
        modal.wait.return_value = True
        active_interaction = Mock()
        active_interaction.response.send_modal = AsyncMock()
        active_interaction.followup.send = AsyncMock()

        with (
            patch.object(workflow, "BuildDataModal", return_value=modal),
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
        ):
            await workflow.SubmitEventDataWorkflow(
                Mock(), Mock(), STORE, GAME, FORMAT, make_event(),
                DataInputEnum.Manual.value, active_interaction, 88, False
            )

        active_interaction.followup.send.assert_awaited_once_with(
            "Data entry timed out. No data from this step was added to "
            "the event results.",
            ephemeral=True,
        )
        save.assert_not_awaited()

    async def test_confirmation_timeout_edits_review_without_persisting(self):
        modal = self.make_modal(DataConverted(None, STANDINGS, None, None, None))
        active_interaction = Mock()
        active_interaction.response.send_modal = AsyncMock()
        review_message = Mock()
        review_message.edit = AsyncMock()
        modal.interaction.followup.send.return_value = review_message
        view = Mock()
        view.wait = AsyncMock(return_value=True)

        with (
            patch.object(workflow, "BuildDataModal", return_value=modal),
            patch.object(workflow, "BuildDataReview", return_value=("review", view)),
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
        ):
            await workflow.SubmitEventDataWorkflow(
                Mock(), Mock(), STORE, GAME, FORMAT, make_event(),
                DataInputEnum.Manual.value, active_interaction, 88, False
            )

        review_message.edit.assert_awaited_once_with(
            content=(
                "Confirmation timed out. This submission was not added "
                "to the event results."
            ),
            view=None,
        )
        save.assert_not_awaited()


class NewEventNotificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_sends_store_and_hub_messages_with_event_details(self):
        bot = Mock()
        interaction = Mock()
        interaction.guild_id = 1234
        interaction.channel_id = 5678
        event = make_event()

        with (
            patch.object(
                workflow, "MessageChannel", new_callable=AsyncMock
            ) as message_channel,
            patch.object(
                workflow, "MessageHubs", new_callable=AsyncMock
            ) as message_hubs,
        ):
            await workflow.NotifyNewEventSubmission(bot, interaction, STORE, event)

        message_channel.assert_awaited_once_with(
            bot,
            "New data for October 19's Weekly Tournament event has been submitted! "
            "Use the `/submit archetype` command to input an archetype!",
            interaction.guild_id,
            interaction.channel_id,
        )
        message_hubs.assert_awaited_once_with(
            bot,
            STORE,
            event,
            "New event submitted for Example Store: "
            "Weekly Tournament (October 19). Waiting for archetypes...",
        )


class SubmitDataCommandTests(unittest.IsolatedAsyncioTestCase):
    def make_interaction(self):
        interaction = Mock()
        interaction.extras = {
            "db_object": SimpleNamespace(
                store=STORE, hub=None, game=GAME, format=FORMAT
            )
        }
        interaction.user.id = 88
        interaction.followup.send = AsyncMock()
        return interaction

    async def test_new_event_is_created_before_workflow_receives_it(self):
        event = make_event(event_id=0)
        active_interaction = Mock()
        interaction = self.make_interaction()
        cog = SubmitDataChecker(Mock())

        with (
            patch(
                "commands.submit_commands.EventForData",
                new_callable=AsyncMock,
                return_value=(event, DataInputEnum.CSV.value, active_interaction, True),
            ),
            patch(
                "commands.submit_commands.CreateEvent",
                new_callable=AsyncMock,
                return_value=42,
            ) as create_event,
            patch(
                "commands.submit_commands.SubmitEventDataWorkflow",
                new_callable=AsyncMock,
            ) as submit_workflow,
        ):
            await SubmitDataChecker.SubmitDataCommand.callback(cog, interaction)

        create_event.assert_awaited_once_with(event, interaction.user.id)
        submit_workflow.assert_awaited_once_with(
            bot=cog.bot,
            interaction=interaction,
            store=STORE,
            game=GAME,
            format=FORMAT,
            event=event._replace(id=42),
            input_type=DataInputEnum.CSV.value,
            active_interaction=active_interaction,
            submitter_id=interaction.user.id,
            is_new_event=True,
        )

    async def test_event_selection_cancellation_stops_before_creation(self):
        interaction = self.make_interaction()
        cog = SubmitDataChecker(Mock())

        with (
            patch(
                "commands.submit_commands.EventForData",
                new_callable=AsyncMock,
                return_value=(None, None, None, False),
            ),
            patch(
                "commands.submit_commands.CreateEvent",
                new_callable=AsyncMock,
            ) as create_event,
            patch(
                "commands.submit_commands.SubmitEventDataWorkflow",
                new_callable=AsyncMock,
            ) as submit_workflow,
        ):
            await SubmitDataChecker.SubmitDataCommand.callback(cog, interaction)

        interaction.followup.send.assert_awaited_once_with(
            "Event canceled!", ephemeral=True
        )
        create_event.assert_not_awaited()
        submit_workflow.assert_not_awaited()

if __name__ == "__main__":
    unittest.main()
