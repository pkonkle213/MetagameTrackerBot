import unittest
from datetime import date
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from PIL import Image

from commands.attendance_command import EventAttendance
from discord import app_commands
from custom_errors import KnownError
from services import store_attendance_graph_services as graph_services
from services import date_functions
from services.date_functions import BuildDateRange


class AttendanceGraphDateRangeTests(unittest.TestCase):
    @patch.object(date_functions, "GetToday", return_value=date(2025, 6, 15))
    def test_defaults_to_one_year_ending_today(self, _today):
        self.assertEqual(
            BuildDateRange("", "", years=1),
            (date(2024, 6, 15), date(2025, 6, 15)),
        )

    def test_defaults_start_date_to_one_year_before_explicit_end_date(self):
        self.assertEqual(
            BuildDateRange("", "02/28/2025", years=1),
            (date(2024, 2, 28), date(2025, 2, 28)),
        )

    def test_clamps_leap_day_when_previous_year_has_no_february_29(self):
        self.assertEqual(
            BuildDateRange("", "02/29/2024", years=1),
            (date(2023, 2, 28), date(2024, 2, 29)),
        )

    def test_rejects_start_after_end(self):
        with self.assertRaises(KnownError):
            BuildDateRange("06/16/2025", "06/15/2025", years=1)

    def test_default_eight_week_behavior_is_unchanged(self):
        self.assertEqual(
            BuildDateRange("", "06/15/2025"),
            (date(2025, 4, 14), date(2025, 6, 15)),
        )


class AttendanceGraphImageTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            (date(2025, 1, 3), "Friday", "Magic", "Standard", 20),
            (date(2025, 1, 10), "Friday", "Magic", "Standard", 25),
            (date(2025, 1, 17), "Friday", "Magic", "Modern", 16),
        ]

    def test_grouping_uses_format_or_game_based_on_channel_mapping(self):
        by_format = graph_services._Series(self.rows, True, False)
        by_game = graph_services._Series(self.rows, False, False)

        self.assertEqual(set(by_format), {"Standard", "Modern"})
        self.assertEqual(set(by_game), {"Magic"})

    def test_creates_png_with_format_scoped_trend(self):
        image_bytes = graph_services.BuildAttendanceGraphImage(
            self.rows, "Store attendance", True, True
        )

        image = Image.open(BytesIO(image_bytes))
        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.size, (graph_services.WIDTH, graph_services.HEIGHT))

    def test_graph_fetches_store_events_with_date_and_channel_scope(self):
        objects = SimpleNamespace(
            store=SimpleNamespace(discord_id=123, store_name="Test Store"),
            game=SimpleNamespace(id=1, game_name="Magic"),
            format=SimpleNamespace(id=2, format_name="Standard"),
        )
        rows = [self.rows[0]]

        with (
            patch.object(
                graph_services,
                "GetStoreAttendanceGraph",
                new=AsyncMock(return_value=rows),
            ) as get_attendance,
            patch.object(
                graph_services, "BuildAttendanceGraphImage", return_value=b"png"
            ) as build_image,
        ):
            result = __import__("asyncio").run(
                graph_services.GetAttendanceGraph(objects, None, "01/10/2025")
            )

        self.assertEqual(result, b"png")
        get_attendance.assert_awaited_once_with(
            objects.store, objects.game, objects.format, date(2024, 1, 10), date(2025, 1, 10)
        )
        build_image.assert_called_once_with(rows, "Test Store attendance: Standard", True, True)

    def test_missing_game_uses_all_games_even_if_format_metadata_exists(self):
        objects = SimpleNamespace(
            store=SimpleNamespace(discord_id=123, store_name="Test Store"),
            game=None,
            format=SimpleNamespace(id=2, format_name="Standard"),
        )

        async def run_graph():
            with (
                patch.object(
                    graph_services,
                    "GetStoreAttendanceGraph",
                    new=AsyncMock(return_value=[self.rows[0]]),
                ) as get_attendance,
                patch.object(
                    graph_services,
                    "BuildAttendanceGraphImage",
                    return_value=b"png",
                ) as build_image,
            ):
                await graph_services.GetAttendanceGraph(objects, None, None)
            return get_attendance, build_image

        get_attendance, build_image = __import__("asyncio").run(run_graph())

        self.assertIsNone(get_attendance.await_args.args[2])
        self.assertFalse(build_image.call_args.args[3])


class AttendanceCommandGroupTests(unittest.TestCase):
    def test_exposes_chart_and_graph_subcommands(self):
        command_names = {
            command.name for command in EventAttendance.__cog_app_commands__
        }
        self.assertEqual(command_names, {"table", "graph"})

    def test_graph_has_optional_start_and_end_dates(self):
        graph = next(
            command
            for command in EventAttendance.__cog_app_commands__
            if command.name == "graph"
        )
        self.assertEqual([parameter.name for parameter in graph.parameters], ["start_date", "end_date"])
        self.assertTrue(all(not parameter.required for parameter in graph.parameters))


class AttendanceGraphRoleTests(unittest.IsolatedAsyncioTestCase):
    async def test_graph_requires_the_mtstore_role(self):
        graph = next(
            command
            for command in EventAttendance.__cog_app_commands__
            if command.name == "graph"
        )
        interaction = SimpleNamespace(
            user=SimpleNamespace(roles=[SimpleNamespace(name="MTStore")])
        )
        await graph.checks[0](interaction)

        interaction.user.roles = [SimpleNamespace(name="Other")]
        with self.assertRaises(app_commands.MissingAnyRole):
            await graph.checks[0](interaction)


if __name__ == "__main__":
    unittest.main()
