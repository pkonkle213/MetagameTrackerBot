import os
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

for environment_key, default_value in {
    "DATABASE_URL": "postgresql://test:test@localhost/test",
    "DISCORD_TOKEN": "test-token",
    "BOT_GUILD_ID": "1",
    "DATA_GUILD_ID": "2",
    "FIVE6_GUILD_ID": "3",
    "BOT_ERROR_ID": "4",
    "BOT_CLAIMSTREAM_ID": "5",
    "BOT_LOG_CHANNELID": "6",
    "BOT_URL_INSTALL": "https://example.com/install",
    "BOT_URL_SOP": "https://example.com/sop",
    "BOT_URL_FEEDBACK": "https://example.com/feedback",
    "PHIL_USERID": "7",
}.items():
    os.environ.setdefault(environment_key, default_value)

from data.personal_history_data import _archetype_search_filter
from services import personal_history_service


class PersonalHistoryFilterTests(unittest.IsolatedAsyncioTestCase):
    def test_archetype_filter_is_case_insensitive_partial_and_parameterized(self):
        clause, parameters = _archetype_search_filter(
            "COALESCE(ua.archetype_played, 'Unknown')", "  blue eyes  "
        )

        self.assertEqual(
            clause,
            "AND COALESCE(ua.archetype_played, 'Unknown') ILIKE %s",
        )
        self.assertEqual(parameters, ["%blue eyes%"])

    def test_archetype_filter_escapes_like_wildcards(self):
        clause, parameters = _archetype_search_filter(
            "COALESCE(ua.archetype_played, 'Unknown')", r"100%_deck"
        )

        self.assertIn("ILIKE %s", clause)
        self.assertEqual(parameters, [r"%100\%\_deck%"])

    def test_blank_archetype_does_not_add_a_query_filter(self):
        self.assertEqual(_archetype_search_filter("ua.archetype_played", "  "), ("", []))

    async def test_archetype_filter_reaches_all_store_and_hub_history_queries(self):
        store = Mock()
        hub = Mock()
        cases = [
            (
                personal_history_service.GetPersonalPairingsHistory,
                "GetStorePairingsHistory",
                SimpleNamespace(
                    store=store, hub=None, game=None, format=None, region=None
                ),
                (23, store, None, None, date(2024, 1, 1), date(2024, 12, 31), "blue"),
            ),
            (
                personal_history_service.GetPersonalPairingsHistory,
                "GetHubPairingsHistory",
                SimpleNamespace(
                    store=None, hub=hub, game=None, format=None, region=None
                ),
                (
                    23,
                    hub,
                    None,
                    None,
                    None,
                    date(2024, 1, 1),
                    date(2024, 12, 31),
                    "blue",
                ),
            ),
            (
                personal_history_service.GetPersonalStandingsHistory,
                "GetStoreStandingsHistory",
                SimpleNamespace(
                    store=store, hub=None, game=None, format=None, region=None
                ),
                (23, store, None, None, date(2024, 1, 1), date(2024, 12, 31), "blue"),
            ),
            (
                personal_history_service.GetPersonalStandingsHistory,
                "GetHubStandingsHistory",
                SimpleNamespace(
                    store=None, hub=hub, game=None, format=None, region=None
                ),
                (
                    23,
                    hub,
                    None,
                    None,
                    None,
                    date(2024, 1, 1),
                    date(2024, 12, 31),
                    "blue",
                ),
            ),
        ]

        for service_function, data_function_name, objects, expected_args in cases:
            with self.subTest(data_function=data_function_name):
                with (
                    patch.object(
                        personal_history_service,
                        "BuildDateRange",
                        return_value=(date(2024, 1, 1), date(2024, 12, 31)),
                    ),
                    patch.object(
                        personal_history_service,
                        "BuildTableOutput",
                        return_value=["history"],
                    ),
                    patch.object(
                        personal_history_service,
                        data_function_name,
                        new_callable=AsyncMock,
                        return_value=[("row",)],
                    ) as history_query,
                ):
                    result = await service_function(
                        23, "01/01/2024", "12/31/2024", objects, "blue"
                    )

                self.assertEqual(result, ["history"])
                history_query.assert_awaited_once_with(*expected_args)


if __name__ == "__main__":
    unittest.main()
