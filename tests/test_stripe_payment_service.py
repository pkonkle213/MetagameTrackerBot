import unittest
from unittest.mock import AsyncMock, patch

from services import stripe_payment_service


class StripePaymentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_checkout_options_use_expected_prices_and_intervals(self):
        checkout_options = (
            ("player", "monthly", 500, "month"),
            ("player", "yearly", 5000, "year"),
            ("store", "monthly", 1000, "month"),
            ("store", "yearly", 10000, "year"),
        )

        for tier, billing_interval, amount, stripe_interval in checkout_options:
            with self.subTest(tier=tier, billing_interval=billing_interval):
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
                        tier=tier,
                        billing_interval=billing_interval,
                discord_user_id=123,
                discord_user_name="test-user",
                discord_guild_id=456,
            )

        self.assertIs(result, session)
        kwargs = run_in_thread.await_args.kwargs
        self.assertNotIn("payment_method_types", kwargs)
        self.assertEqual(kwargs["mode"], "subscription")
                price_data = kwargs["line_items"][0]["price_data"]
                self.assertEqual(price_data["unit_amount"], amount)
                self.assertEqual(price_data["recurring"]["interval"], stripe_interval)
                self.assertEqual(kwargs["metadata"]["billing_interval"], stripe_interval)

    async def test_rejects_hub_and_unknown_billing_interval(self):
        with self.assertRaisesRegex(ValueError, "Unknown subscription tier"):
                    await stripe_payment_service.create_subscription_session(
                tier="hub",
                billing_interval="monthly",
                        discord_user_id=123,
                        discord_user_name="test-user",
                        discord_guild_id=456,
                    )

        with self.assertRaisesRegex(ValueError, "Unknown subscription tier"):
                    await stripe_payment_service.create_subscription_session(
                tier="player",
                billing_interval="weekly",
                        discord_user_id=123,
                        discord_user_name="test-user",
                        discord_guild_id=456,
                    )


if __name__ == "__main__":
    unittest.main()
