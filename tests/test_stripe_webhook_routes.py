import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import AsyncMock, Mock, patch

from aiohttp.test_utils import TestClient, TestServer

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

from services import stripe_webhook_service


class StripeWebhookRouteTests(unittest.IsolatedAsyncioTestCase):
    signing_secret = "whsec_test_signing_secret"
    event_payload = json.dumps(
        {
            "id": "evt_test",
            "object": "event",
            "type": "payment_intent.created",
            "data": {"object": {"id": "pi_test"}},
        },
        separators=(",", ":"),
    )

    async def asyncSetUp(self):
        self.bot = Mock()
        self.client = TestClient(TestServer(stripe_webhook_service.create_web_app(self.bot)))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()

    def make_signature(self, payload: str) -> str:
        timestamp = int(time.time())
        signed_payload = f"{timestamp}.{payload}".encode("utf-8")
        signature = hmac.new(
            self.signing_secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        return f"t={timestamp},v1={signature}"

    async def test_accepts_valid_signed_test_event(self):
        with patch.object(
            stripe_webhook_service.settings,
            "STRIPE_WEBHOOK_SECRET",
            self.signing_secret,
        ):
            response = await self.client.post(
                "/stripe/webhook",
                data=self.event_payload,
                headers={"Stripe-Signature": self.make_signature(self.event_payload)},
            )

        self.assertEqual(response.status, 200)
        self.assertEqual(await response.text(), "OK")

    async def test_rejects_invalid_signature(self):
        with patch.object(
            stripe_webhook_service.settings,
            "STRIPE_WEBHOOK_SECRET",
            self.signing_secret,
        ):
            response = await self.client.post(
                "/stripe/webhook",
                data=self.event_payload,
                headers={"Stripe-Signature": "t=1,v1=invalid"},
            )

        self.assertEqual(response.status, 400)
        self.assertEqual(await response.text(), "Invalid signature")

    async def test_completed_subscription_records_payment_and_deduplicates_retries(self):
        subscription_id = "sub_test"
        user_id = "12345"
        guild_id = "67890"
        checkout_session = {
            "id": "cs_test",
            "mode": "subscription",
            "payment_status": "paid",
            "amount_total": 1000,
            "subscription": subscription_id,
            "metadata": {
                "discord_user_id": user_id,
                "discord_user_name": "test-user",
                "discord_guild_id": guild_id,
                "tier": "store",
            },
        }
        event_payload = json.dumps(
            {
                "id": "evt_checkout",
                "object": "event",
                "type": "checkout.session.completed",
                "created": 1_800_000_000,
                "data": {"object": checkout_session},
            },
            separators=(",", ":"),
        )
        subscriber = Mock()
        subscriber.send = AsyncMock()
        self.bot.fetch_user = AsyncMock(return_value=subscriber)
        subscription = {
            "id": subscription_id,
            "current_period_start": 1_800_000_000,
            "current_period_end": 1_802_592_000,
            "items": {
                "data": [
                    {
                        "price": {
                            "recurring": {"interval": "month", "interval_count": 1}
                        }
                    }
                ]
            },
        }

        with (
            patch.object(
                stripe_webhook_service.settings,
                "STRIPE_WEBHOOK_SECRET",
                self.signing_secret,
            ),
            patch.object(
                stripe_webhook_service.settings,
                "STRIPE_SECRET_KEY",
                "sk_test_placeholder",
            ),
            patch.object(
                stripe_webhook_service.stripe.Subscription,
                "retrieve",
                return_value=subscription,
            ),
            patch.object(
                stripe_webhook_service,
                "RecordStripePayment",
                new_callable=AsyncMock,
                side_effect=[True, False],
            ) as record_payment,
        ):
            response = await self.client.post(
                "/stripe/webhook",
                data=event_payload,
                headers={"Stripe-Signature": self.make_signature(event_payload)},
            )
            retry_response = await self.client.post(
                "/stripe/webhook",
                data=event_payload,
                headers={"Stripe-Signature": self.make_signature(event_payload)},
            )

        self.assertEqual(response.status, 200)
        self.assertEqual(retry_response.status, 200)
        self.assertEqual(record_payment.await_count, 2)
        payment_fields = record_payment.await_args.kwargs
        self.assertEqual(payment_fields["stripe_event_id"], "evt_checkout")
        self.assertEqual(payment_fields["stripe_checkout_session_id"], "cs_test")
        self.assertEqual(payment_fields["stripe_subscription_id"], subscription_id)
        self.assertEqual(payment_fields["user_id"], int(user_id))
        self.assertEqual(payment_fields["discord_id"], int(guild_id))
        self.assertEqual(payment_fields["subscription_level"], "store")
        self.assertEqual(payment_fields["billing_interval"], "Every 1 month")
        self.assertEqual(payment_fields["period_start"].timestamp(), 1_800_000_000)
        self.assertEqual(payment_fields["period_end"].timestamp(), 1_802_592_000)
        self.assertEqual(str(payment_fields["amount"]), "10")
        self.bot.fetch_user.assert_awaited_once_with(int(user_id))
        subscriber.send.assert_awaited_once()

    async def test_serves_homepage_and_legal_get_routes(self):
        health_response = await self.client.get("/")
        privacy_response = await self.client.get("/privacy")
        terms_response = await self.client.get("/terms")

        self.assertEqual(health_response.status, 200)
        homepage = await health_response.text()
        self.assertIn("Metagame Tracker Bot", homepage)
        self.assertIn('href="/privacy"', homepage)
        self.assertIn('href="/terms"', homepage)
        self.assertEqual(privacy_response.status, 200)
        self.assertIn("text/html", privacy_response.headers["Content-Type"])
        self.assertEqual(terms_response.status, 200)
        self.assertIn("text/html", terms_response.headers["Content-Type"])


if __name__ == "__main__":
    unittest.main()
