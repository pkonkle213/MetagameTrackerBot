import unittest
from unittest.mock import AsyncMock, patch

from services import stripe_payment_service


class StripePaymentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_yearly_player_checkout_uses_yearly_price_and_dynamic_methods(self):
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
                billing_period="yearly",
                discord_user_id=123,
                discord_user_name="test-user",
                discord_guild_id=456,
            )

        self.assertIs(result, session)
        kwargs = run_in_thread.await_args.kwargs
        self.assertNotIn("payment_method_types", kwargs)
        self.assertEqual(kwargs["mode"], "subscription")
        self.assertEqual(
            kwargs["line_items"][0]["price_data"]["unit_amount"], 5000
        )
        self.assertEqual(
            kwargs["line_items"][0]["price_data"]["recurring"]["interval"], "year"
        )
        self.assertEqual(
            kwargs["subscription_data"]["metadata"],
            {
                "discord_user_id": "123",
                "discord_user_name": "test-user",
                "discord_guild_id": "456",
                "tier": "player",
                "billing_period": "yearly",
            },
        )

    async def test_all_player_and_store_prices_match_requested_billing_periods(self):
        expected = {
            ("player", "monthly"): (500, "month"),
            ("player", "yearly"): (5000, "year"),
            ("store", "monthly"): (1000, "month"),
            ("store", "yearly"): (10000, "year"),
        }
        for (tier, period), (amount, interval) in expected.items():
            with self.subTest(tier=tier, period=period):
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
                    await stripe_payment_service.create_subscription_session(
                        tier=tier,
                        billing_period=period,
                        discord_user_id=123,
                        discord_user_name="test-user",
                        discord_guild_id=456,
                    )

                request = run_in_thread.await_args.kwargs["line_items"][0]["price_data"]
                self.assertEqual(request["unit_amount"], amount)
                self.assertEqual(request["recurring"]["interval"], interval)

    async def test_hub_and_unknown_billing_period_are_not_available(self):
        for tier, period in (("hub", "monthly"), ("player", "quarterly")):
            with self.subTest(tier=tier, period=period):
                with self.assertRaises(ValueError):
                    await stripe_payment_service.create_subscription_session(
                        tier=tier,
                        billing_period=period,
                        discord_user_id=123,
                        discord_user_name="test-user",
                        discord_guild_id=456,
                    )


if __name__ == "__main__":
    unittest.main()
