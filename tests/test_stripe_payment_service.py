import unittest
from unittest.mock import AsyncMock, patch

from services import stripe_payment_service


class StripePaymentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_subscription_checkout_leaves_payment_methods_dynamic(self):
        session = object()

        with (
            patch.object(
                stripe_payment_service.settings,
                "STRIPE_SECRET_KEY",
                "sk_test_placeholder",
            ),
            patch.object(
                stripe_payment_service.asyncio,
                "to_thread",
                new_callable=AsyncMock,
                return_value=session,
            ) as run_in_thread,
        ):
            result = await stripe_payment_service.create_subscription_session(
                tier="player",
                discord_user_id=123,
                discord_user_name="test-user",
                discord_guild_id=456,
            )

        self.assertIs(result, session)
        kwargs = run_in_thread.await_args.kwargs
        self.assertNotIn("payment_method_types", kwargs)
        self.assertEqual(kwargs["mode"], "subscription")
        self.assertEqual(
            kwargs["subscription_data"]["metadata"],
            {
                "discord_user_id": "123",
                "discord_user_name": "test-user",
                "discord_guild_id": "456",
                "tier": "player",
            },
        )


if __name__ == "__main__":
    unittest.main()
