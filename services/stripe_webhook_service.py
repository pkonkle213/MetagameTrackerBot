from datetime import datetime, timezone
from decimal import Decimal

import stripe
import discord
from aiohttp import web
import settings
from data import payments_data
from legal_pages import get_legal_page


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
    object_id = value.get('id')
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


async def handle_stripe_webhook(request: web.Request, bot: discord.Client) -> web.Response:
  payload = await request.read()
  sig_header = request.headers.get('Stripe-Signature', '')

  if not settings.STRIPE_WEBHOOK_SECRET:
    return web.Response(status=503, text='Webhook is not configured')
  if not sig_header:
    return web.Response(status=400, text='Missing Stripe signature')

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    ).to_dict()
  except (stripe.SignatureVerificationError, ValueError):
    print('Invalid Stripe webhook signature')
    return web.Response(status=400, text='Invalid signature')
  except stripe.StripeError:
    print('Unable to validate Stripe webhook')
    return web.Response(status=400, text='Invalid webhook')

  if event.get('type') == 'checkout.session.completed':
    session = event.get('data', {}).get('object', {})
    if session.get('mode') != 'subscription' or session.get('payment_status') != 'paid':
      return web.Response(status=200, text='OK')
    metadata = session.get('metadata') or {}

    discord_user_id = metadata.get('discord_user_id')
    discord_guild_id = metadata.get('discord_guild_id')
    discord_user_name = metadata.get('discord_user_name', 'Unknown')
    tier = metadata.get('tier', 'Unknown').title()

    event_id = event.get('id')
    session_id = session.get('id')
    if not isinstance(event_id, str) or not isinstance(session_id, str):
      return web.Response(status=400, text='Invalid checkout event')

    inserted = await payments_data.RecordPayment(
      discord_id=_optional_discord_id(discord_guild_id),
      user_id=_optional_discord_id(discord_user_id),
      payment_date=_stripe_event_datetime(event.get('created')),
      amount=_usd_amount_from_minor_units(session.get('amount_total')),
      checkout_session_id=session_id,
      subscription_id=_stripe_object_id(session.get('subscription')),
      subscription_level=metadata.get('tier'),
      billing_interval=metadata.get('billing_interval'),
      stripe_event_id=event_id,
    )

    if inserted and isinstance(discord_user_id, str) and discord_user_id.isdigit():
      try:
        user = await bot.fetch_user(int(discord_user_id))
        await user.send(
          f"Thank you for subscribing, **{discord_user_name}**!\n\n"
          f"Here's your confirmation:\n"
          f"> **Tier:** {tier}\n"
          f"> **Your Discord ID:** `{discord_user_id}`\n"
          f"> **Server ID:** `{discord_guild_id}`\n\n"
          f"If you have any questions, please reach out to the server owner."
        )
        print(f'Thank-you DM sent to user {discord_user_id}')
      except Exception as e:
        print(f'Failed to send Stripe confirmation DM: {type(e).__name__}')

  return web.Response(status=200, text='OK')


async def handle_health_and_legal(request: web.Request) -> web.Response:
  legal_page = get_legal_page(request.path)
  if legal_page is None:
    raise web.HTTPNotFound()

  content_type, page_content = legal_page
  return web.Response(
    status=200,
    body=page_content,
    headers={
      'Content-Type': content_type,
      'X-Content-Type-Options': 'nosniff',
    },
  )


def create_web_app(bot: discord.Client) -> web.Application:
  app = web.Application()

  async def stripe_webhook_route(request: web.Request) -> web.Response:
    return await handle_stripe_webhook(request, bot)

  app.router.add_post('/stripe/webhook', stripe_webhook_route)
  app.router.add_get('/{path:.*}', handle_health_and_legal)
  return app


async def start_webhook_server(
  bot: discord.Client, port: int = settings.HTTP_SERVER_PORT
) -> web.AppRunner:
  app = create_web_app(bot)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', port)
  await site.start()
  print(f'Health and Stripe webhook server listening on port {port}')
  return runner
