import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
from api_calls import melee_tournaments
from custom_errors import KnownError
from tuple_conversions import Store


STORE = Store(1234, "Example Store", "Example Store", 1, "Owner", "", True, 1, True)


class MeleeTournamentApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_event_details_uses_tournament_endpoint_and_store_credentials(self):
        response = Mock(status=200)
        response.json = AsyncMock(return_value={
            "Name": "Weekly Event",
            "LastPairDateTime": "2026-10-19T02:30:00Z",
            "ID": 321,
        })
        request_context = Mock()
        request_context.__aenter__ = AsyncMock(return_value=response)
        request_context.__aexit__ = AsyncMock(return_value=None)
        session = Mock()
        session.get = Mock(return_value=request_context)
        session_context = Mock()
        session_context.__aenter__ = AsyncMock(return_value=session)
        session_context.__aexit__ = AsyncMock(return_value=None)

        with (
            patch.object(
                melee_tournaments,
                "GetStoreMeleeInfo",
                new_callable=AsyncMock,
                return_value=SimpleNamespace(
                    melee_client_id="client-id",
                    melee_client_secret="client-secret",
                ),
            ),
            patch.object(
                melee_tournaments.aiohttp,
                "ClientSession",
                return_value=session_context,
            ),
        ):
            details = await melee_tournaments.GetMeleeTournamentDetails("321", STORE)

        session.get.assert_called_once_with(
            "https://melee.gg/api/tournament/321",
            auth=aiohttp.BasicAuth("client-id", "client-secret"),
        )
        self.assertEqual(details["Name"], "Weekly Event")

    async def test_details_failure_refetches_pairings_for_replacement(self):
        first_pairings = [{"round": 1}]
        refreshed_pairings = [{"round": 1}, {"round": 2}]
        with (
            patch.object(
                melee_tournaments,
                "GetMeleeTournamentPairings",
                new_callable=AsyncMock,
                side_effect=[first_pairings, refreshed_pairings],
            ) as get_pairings,
            patch.object(
                melee_tournaments,
                "GetMeleeTournamentDetails",
                new_callable=AsyncMock,
                side_effect=KnownError("Details unavailable"),
            ),
        ):
            result = await melee_tournaments.GetMeleeTournamentData("321", STORE)

        self.assertEqual(result.pairings, refreshed_pairings)
        self.assertIsNone(result.event_details)
        self.assertEqual(result.event_details_error, "Details unavailable")
        self.assertEqual(get_pairings.await_count, 2)
