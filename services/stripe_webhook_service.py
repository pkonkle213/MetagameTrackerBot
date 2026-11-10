from datetime import datetime, timezone
from decimal import Decimal

import stripe
import discord
from aiohttp import web

import settings
from data import payments_data
from legal_pages import get_legal_page
import timedposts.automated_paid_users as apu


def _optional_discord_id(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _stripe_object_id(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        object_id = value.get("id")
        return object_id if isinstance(object_id, str) else None
    return None


def _usd_amount_from_minor_units(value: object) -> Decimal | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return Decimal(value) / Decimal(100)
    return None


def _stripe_event_datetime(value: object) -> datetime | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)
    return None


async def _send_payment_confirmation_to_channel(
    bot: discord.Client, message: str
) -> None:
    try:
        channel = bot.get_channel(settings.PAYMENT_CONFIRMATION_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(
                settings.PAYMENT_CONFIRMATION_CHANNEL_ID
            )

        channel_guild_id = getattr(getattr(channel, "guild", None), "id", None)
        if channel_guild_id != settings.PAYMENT_CONFIRMATION_GUILD_ID:
            print("Stripe confirmation channel is not in the configured guild")
            return

        await channel.send(message)
        print("Stripe payment confirmation sent to configured channel")
    except Exception as error:
        print(
            "Failed to send Stripe payment confirmation to configured channel: "
            f"{type(error).__name__}"
        )


async def handle_stripe_webhook(
    request: web.Request, bot: discord.Client
) -> web.Response:
    payload = await request.read()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        return web.Response(status=503, text="Webhook is not configured")
    if not sig_header:
        return web.Response(status=400, text="Missing Stripe signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        ).to_dict()
    except (stripe.SignatureVerificationError, ValueError):
        print("Invalid Stripe webhook signature")
        return web.Response(status=400, text="Invalid signature")
    except stripe.StripeError:
        print("Unable to validate Stripe webhook")
        return web.Response(status=400, text="Invalid webhook")

    if event.get("type") == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        if (
            session.get("mode") != "subscription"
            or session.get("payment_status") != "paid"
        ):
            return web.Response(status=200, text="OK")

        metadata = session.get("metadata") or {}
        discord_user_id = metadata.get("discord_user_id")
        discord_guild_id = metadata.get("discord_guild_id")
        discord_user_name = metadata.get("discord_user_name", "Unknown")
        tier = metadata.get("tier", "Unknown").title()
        billing_interval = metadata.get("billing_interval")

        event_id = event.get("id")
        session_id = session.get("id")
        if not isinstance(event_id, str) or not isinstance(session_id, str):
            return web.Response(status=400, text="Invalid checkout event")

        amount = _usd_amount_from_minor_units(session.get("amount_total"))
        inserted = await payments_data.RecordPayment(
            discord_id=_optional_discord_id(discord_guild_id),
            user_id=_optional_discord_id(discord_user_id),
            payment_date=_stripe_event_datetime(event.get("created")),
            amount=amount,
            checkout_session_id=session_id,
            subscription_id=_stripe_object_id(session.get("subscription")),
            subscription_level=metadata.get("tier"),
            billing_interval=billing_interval,
            stripe_event_id=event_id,
        )

        if inserted:
            if metadata.get("tier") == "store":
                await apu.UpdatePaidStores()
            elif metadata.get("tier") == "player":
                await apu.UpdatePaidUsers()

            if isinstance(discord_user_id, str) and discord_user_id.isdigit():
                try:
                    user = await bot.fetch_user(int(discord_user_id))
                    await user.send(
                        f"Thank you for subscribing, **{discord_user_name}**!\n\n"
                        "Here's your confirmation:\n"
                        f"> **Tier:** {tier}\n"
                        f"> **Your Discord ID:** `{discord_user_id}`\n"
                        f"> **Server ID:** `{discord_guild_id}`\n\n"
                        "If you have any questions, please reach out to "
                        "metagametrackerbot@gmail.com."
                    )
                    print(f"Thank-you DM sent to user {discord_user_id}")
                except Exception as error:
                    print(
                        "Failed to send Stripe confirmation DM: "
                        f"{type(error).__name__}"
                    )

            amount_label = f"${amount:.2f}" if amount is not None else "Unknown amount"
            interval_label = {
                "month": "Monthly",
                "year": "Yearly",
            }.get(billing_interval, "Unknown billing interval")
            user_label = (
                f"<@{discord_user_id}> (`{discord_user_id}`)"
                if isinstance(discord_user_id, str) and discord_user_id.isdigit()
                else discord_user_name
            )
            await _send_payment_confirmation_to_channel(
                bot,
                "Stripe subscription payment completed\n"
                f"> **Customer:** {user_label}\n"
                f"> **Tier:** {tier}\n"
                f"> **Billing:** {interval_label} ({amount_label} USD)\n"
                f"> **Discord server ID:** `{discord_guild_id}`\n"
                f"> **Checkout session:** `{session_id}`\n"
                f"> **Subscription:** "
                f"`{_stripe_object_id(session.get('subscription'))}`",
            )

    return web.Response(status=200, text="OK")


async def handle_health_and_legal(request: web.Request) -> web.Response:
    legal_page = get_legal_page(request.path)
    if legal_page is None:
        raise web.HTTPNotFound()

    content_type, page_content = legal_page
    return web.Response(
        status=200,
        body=page_content,
        headers={
            "Content-Type": content_type,
            "X-Content-Type-Options": "nosniff",
        },
    )


def create_web_app(bot: discord.Client) -> web.Application:
    app = web.Application()

    async def stripe_webhook_route(request: web.Request) -> web.Response:
        return await handle_stripe_webhook(request, bot)

    app.router.add_post("/stripe/webhook", stripe_webhook_route)
    app.router.add_get("/{path:.*}", handle_health_and_legal)
    return app


async def start_webhook_server(
    bot: discord.Client, port: int = settings.HTTP_SERVER_PORT
) -> web.AppRunner:
    app = create_web_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Health and Stripe webhook server listening on port {port}")
    return runner
