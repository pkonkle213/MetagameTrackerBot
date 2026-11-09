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

    async def test_persists_paid_subscription_checkout_details(self):
        event = {
            "id": "evt_checkout",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_checkout",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "amount_total": 1000,
                    "subscription": "sub_test",
                    "metadata": {
                        "discord_user_id": "123456",
                        "discord_guild_id": "654321",
                        "discord_user_name": "Test User",
                        "tier": "store",
                    },
                }
            },
        }
        self.bot.fetch_user = AsyncMock()
        self.bot.fetch_user.return_value.send = AsyncMock()

        with (
            patch.object(
                stripe_webhook_service.settings,
                "STRIPE_WEBHOOK_SECRET",
                self.signing_secret,
            ),
            patch.object(
                stripe_webhook_service.stripe.Webhook,
                "construct_event",
                return_value=Mock(to_dict=lambda: event),
            ),
            patch.object(
                stripe_webhook_service.payments_data,
                "RecordPayment",
                new_callable=AsyncMock,
                return_value=True,
            ) as record_payment,
        ):
            response = await self.client.post(
                "/stripe/webhook",
                data="{}",
                headers={"Stripe-Signature": "test-signature"},
            )

        self.assertEqual(response.status, 200)
        record_payment.assert_awaited_once_with(
            discord_id=654321,
            user_id=123456,
            amount=1000,
            checkout_session_id="cs_test_checkout",
            subscription_id="sub_test",
            stripe_event_id="evt_checkout",
        )
        self.bot.fetch_user.assert_awaited_once_with(123456)
        self.bot.fetch_user.return_value.send.assert_awaited_once()

    async def test_duplicate_checkout_event_is_not_notified_again(self):
        event = {
            "id": "evt_duplicate",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_duplicate",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "amount_total": 500,
                    "subscription": "sub_duplicate",
                    "metadata": {"discord_user_id": "123456"},
                }
            },
        }
        self.bot.fetch_user = AsyncMock()

        with (
            patch.object(
                stripe_webhook_service.settings,
                "STRIPE_WEBHOOK_SECRET",
                self.signing_secret,
            ),
            patch.object(
                stripe_webhook_service.stripe.Webhook,
                "construct_event",
                return_value=Mock(to_dict=lambda: event),
            ),
            patch.object(
                stripe_webhook_service.payments_data,
                "RecordPayment",
                new_callable=AsyncMock,
                return_value=False,
            ) as record_payment,
        ):
            response = await self.client.post(
                "/stripe/webhook",
                data="{}",
                headers={"Stripe-Signature": "test-signature"},
            )

        self.assertEqual(response.status, 200)
        record_payment.assert_awaited_once()
        self.bot.fetch_user.assert_not_awaited()

    async def test_skips_unpaid_checkout_without_recording_payment(self):
        event = {
            "id": "evt_unpaid",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_unpaid",
                    "mode": "subscription",
                    "payment_status": "unpaid",
                }
            },
        }

        with (
            patch.object(
                stripe_webhook_service.settings,
                "STRIPE_WEBHOOK_SECRET",
                self.signing_secret,
            ),
            patch.object(
                stripe_webhook_service.stripe.Webhook,
                "construct_event",
                return_value=Mock(to_dict=lambda: event),
            ),
            patch.object(
                stripe_webhook_service.payments_data,
                "RecordPayment",
                new_callable=AsyncMock,
            ) as record_payment,
        ):
            response = await self.client.post(
                "/stripe/webhook",
                data="{}",
                headers={"Stripe-Signature": "test-signature"},
            )

        self.assertEqual(response.status, 200)
        record_payment.assert_not_awaited()

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
