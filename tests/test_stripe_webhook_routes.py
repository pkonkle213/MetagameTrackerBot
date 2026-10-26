import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import Mock, patch

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

    async def test_preserves_health_and_legal_get_routes(self):
        health_response = await self.client.get("/")
        privacy_response = await self.client.get("/privacy")
        terms_response = await self.client.get("/terms")

        self.assertEqual(health_response.status, 200)
        self.assertEqual(await health_response.text(), "OK")
        self.assertEqual(privacy_response.status, 200)
        self.assertIn("text/html", privacy_response.headers["Content-Type"])
        self.assertEqual(terms_response.status, 200)
        self.assertIn("text/html", terms_response.headers["Content-Type"])


if __name__ == "__main__":
    unittest.main()
