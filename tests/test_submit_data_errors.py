import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from custom_errors import KnownError
from input_modals import submit_csv_modal, submit_data_modal, submit_melee_modal
from services import submit_data_workflow as workflow
from tuple_conversions import DataConverted, Event, Store


def make_event() -> Event:
    return Event(
        17,
        None,
        None,
        1234,
        date(2026, 10, 19),
        1,
        2,
        0,
        1,
        "Weekly Tournament",
        1,
        10,
        None,
        False,
    )


STORE = Store(1234, "Example Store", "Example Store", 1, "Owner", "", True, 1, True)


def make_interaction():
    interaction = Mock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


class SubmissionModalErrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_csv_modal_accepts_and_processes_ten_files(self):
        modal = submit_csv_modal.SubmitCSVDataModal(make_event(), "/upload/input.csv")
        uploads = [Mock() for _ in range(10)]
        self.assertEqual(modal.csv_data.component.max_values, 10)
        modal.csv_data = SimpleNamespace(
            component=SimpleNamespace(values=uploads, max_values=10)
        )
        interaction = make_interaction()

        async def convert_csv(_event, file_path, upload):
            return DataConverted(
                [upload],
                None,
                None,
                None,
                None,
                (file_path,),
            )

        with patch.object(
            submit_csv_modal,
            "ConvertAndUploadCSV",
            new_callable=AsyncMock,
            side_effect=convert_csv,
        ) as convert:
            await modal.on_submit(interaction)

        self.assertEqual(convert.await_count, 10)
        upload_paths = [call.args[1] for call in convert.await_args_list]
        self.assertEqual(len(set(upload_paths)), 10)
        self.assertEqual(modal.converted_data.pairings_data, uploads)
        self.assertEqual(modal.converted_data.staged_source_files, tuple(upload_paths))
        self.assertFalse(modal.conversion_failed)

    async def test_csv_conversion_failure_is_reported_and_marked_failed(self):
        modal = submit_csv_modal.SubmitCSVDataModal(make_event(), "/upload/input.csv")
        modal.csv_data = SimpleNamespace(component=SimpleNamespace(values=[Mock()]))
        interaction = make_interaction()

        with patch.object(
            submit_csv_modal,
            "ConvertAndUploadCSV",
            new_callable=AsyncMock,
            side_effect=KnownError("Unable to parse data. Please try again."),
        ):
            await modal.on_submit(interaction)

        self.assertTrue(modal.conversion_failed)
        interaction.followup.send.assert_awaited_once_with(
            "Could not process your CSV submission: "
            "Unable to parse data. Please try again. No event results were saved.",
            ephemeral=True,
        )

    async def test_csv_rejects_multiple_standings_files(self):
        modal = submit_csv_modal.SubmitCSVDataModal(make_event(), "/upload/input.csv")
        uploads = [Mock(), Mock()]
        modal.csv_data = SimpleNamespace(component=SimpleNamespace(values=uploads))
        standings = DataConverted(None, [Mock()], None, None, None)
        interaction = make_interaction()

        with patch.object(
            submit_csv_modal,
            "ConvertAndUploadCSV",
            new_callable=AsyncMock,
            return_value=standings,
        ):
            await modal.on_submit(interaction)

        self.assertTrue(modal.conversion_failed)
        self.assertIn(
            "A standings CSV must be submitted by itself",
            interaction.followup.send.await_args.args[0],
        )
        self.assertIn(
            "No event results were saved.",
            interaction.followup.send.await_args.args[0],
        )

    async def test_manual_conversion_failure_is_reported(self):
        modal = submit_data_modal.SubmitManualDataModal(make_event(), "/upload/input.txt")
        modal.manual_data = SimpleNamespace(
            component=SimpleNamespace(value="invalid input")
        )
        interaction = make_interaction()

        with patch.object(
            submit_data_modal,
            "ConvertAndUploadMessage",
            side_effect=KnownError("Unable to parse data. Please try again."),
        ):
            await modal.on_submit(interaction)

        self.assertTrue(modal.conversion_failed)
        interaction.followup.send.assert_awaited_once()
        self.assertIn(
            "Unable to parse data",
            interaction.followup.send.await_args.args[0],
        )

    async def test_melee_lookup_failure_is_reported(self):
        modal = submit_melee_modal.SubmitMeleeDataModal(
            STORE, make_event(), "/upload/input.json"
        )
        modal.melee_data = SimpleNamespace(value="tournament")
        interaction = make_interaction()

        with patch.object(
            submit_melee_modal,
            "ConvertAndUploadMeleeTournament",
            new_callable=AsyncMock,
            side_effect=KnownError("No data found for this tournament."),
        ):
            await modal.on_submit(interaction)

        self.assertTrue(modal.conversion_failed)
        interaction.followup.send.assert_awaited_once()
        self.assertIn(
            "No data found for this tournament",
            interaction.followup.send.await_args.args[0],
        )

    async def test_unexpected_error_is_logged_and_details_are_not_exposed(self):
        modal = submit_data_modal.SubmitManualDataModal(make_event(), "/upload/input.txt")
        modal.manual_data = SimpleNamespace(
            component=SimpleNamespace(value="some data")
        )
        interaction = make_interaction()

        with (
            patch.object(
                submit_data_modal,
                "ConvertAndUploadMessage",
                side_effect=RuntimeError("internal storage detail"),
            ),
            self.assertLogs("services.submit_data_errors", level="ERROR") as logs,
        ):
            await modal.on_submit(interaction)

        self.assertTrue(modal.conversion_failed)
        message = interaction.followup.send.await_args.args[0]
        self.assertIn("An unexpected error occurred", message)
        self.assertIn("No event results were saved.", message)
        self.assertNotIn("internal storage detail", message)
        self.assertIn("internal storage detail", "\n".join(logs.output))

    async def test_failed_modal_does_not_enter_review_or_save(self):
        modal = Mock()
        modal.conversion_failed = True
        modal.converted_data = DataConverted(None, None, None, None, None)
        modal.wait = AsyncMock(return_value=False)
        active_interaction = Mock()
        active_interaction.response.send_modal = AsyncMock()

        with (
            patch.object(workflow, "BuildDataModal", return_value=modal),
            patch.object(workflow, "BuildDataReview") as build_review,
            patch.object(
                workflow, "SaveDataSubmission", new_callable=AsyncMock
            ) as save,
        ):
            await workflow.SubmitEventDataWorkflow(
                Mock(),
                Mock(),
                STORE,
                Mock(),
                Mock(),
                make_event(),
                1,
                active_interaction,
                88,
                False,
            )

        build_review.assert_not_called()
        save.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
