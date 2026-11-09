import unittest
from unittest.mock import AsyncMock, patch

from data import payments_data


class FakeCursor:
    def __init__(self, returned_row):
        self.returned_row = returned_row
        self.command = None
        self.parameters = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def execute(self, command, parameters):
        self.command = command
        self.parameters = parameters

    async def fetchone(self):
        return self.returned_row


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    def cursor(self):
        return self.fake_cursor


class PaymentsDataTests(unittest.IsolatedAsyncioTestCase):
    async def test_insert_uses_event_id_conflict_guard(self):
        cursor = FakeCursor(("evt_123",))
        connection = FakeConnection(cursor)

        with patch.object(
            payments_data.AsyncConnection,
            "connect",
            new_callable=AsyncMock,
            return_value=connection,
        ):
            inserted = await payments_data.RecordPayment(
                discord_id=456,
                user_id=123,
                amount=1000,
                checkout_session_id="cs_123",
                subscription_id="sub_123",
                stripe_event_id="evt_123",
            )

        self.assertTrue(inserted)
        self.assertIn("ON CONFLICT (stripe_event_id) DO NOTHING", cursor.command)
        self.assertEqual(
            cursor.parameters,
            (456, 123, 1000, "cs_123", "sub_123", "evt_123"),
        )

    async def test_duplicate_event_returns_false(self):
        cursor = FakeCursor(None)
        connection = FakeConnection(cursor)

        with patch.object(
            payments_data.AsyncConnection,
            "connect",
            new_callable=AsyncMock,
            return_value=connection,
        ):
            inserted = await payments_data.RecordPayment(
                discord_id=456,
                user_id=123,
                amount=1000,
                checkout_session_id="cs_123",
                subscription_id="sub_123",
                stripe_event_id="evt_123",
            )

        self.assertFalse(inserted)


if __name__ == "__main__":
    unittest.main()
