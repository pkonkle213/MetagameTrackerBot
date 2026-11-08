import asyncio
from datetime import UTC, datetime
from decimal import Decimal

import stripe
import discord
from aiohttp import web
import settings
from data.payments_data import RecordStripePayment
from legal_pages import get_legal_page


def _subscription_period(
  subscription: dict,
) -> tuple[str, str, datetime, datetime]:
  items = subscription.get('items', {}).get('data', [])
  first_item = items[0] if items else {}
  price = first_item.get('price', {})
  recurring = price.get('recurring', {})
  interval = recurring.get('interval')
  interval_count = recurring.get('interval_count', 1)

  if interval:
    interval_name = interval.replace('_', ' ')
    billing_frequency = (
      f"Every {interval_count} {interval_name}{'s' if interval_count != 1 else ''}"
    )
  else:
    billing_frequency = 'Recurring subscription'

  period_start = subscription.get('current_period_start')
  period_end = subscription.get('current_period_end')
  if period_start is None:
    period_start = first_item.get('current_period_start')
  if period_end is None:
    period_end = first_item.get('current_period_end')

  if period_start is None or period_end is None:
    raise ValueError('Stripe subscription is missing billing-period dates')

  period_start_date = datetime.fromtimestamp(int(period_start), tz=UTC)
  period_end_date = datetime.fromtimestamp(int(period_end), tz=UTC)
  period = (
    f"<t:{int(period_start)}:d> – <t:{int(period_end)}:d>"
  )

  return billing_frequency, period, period_start_date, period_end_date


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

  if event.get('type') in {
    'checkout.session.completed',
    'checkout.session.async_payment_succeeded',
  }:
    session = event.get('data', {}).get('object', {})
    if session.get('mode') != 'subscription' or session.get('payment_status') != 'paid':
      return web.Response(status=200, text='OK')
    metadata = session.get('metadata') or {}

    discord_user_id = metadata.get('discord_user_id')
    discord_guild_id = metadata.get('discord_guild_id')
    discord_user_name = metadata.get('discord_user_name', 'Unknown')
    tier = metadata.get('tier', 'Unknown').title()
    subscription_id = session.get('subscription')
    if isinstance(subscription_id, dict):
      subscription_id = subscription_id.get('id')

    if not subscription_id or not settings.STRIPE_SECRET_KEY:
      print('Stripe checkout completed without subscription details configuration')
      return web.Response(status=503, text='Subscription details unavailable')

    try:
      stripe.api_key = settings.STRIPE_SECRET_KEY
      subscription = await asyncio.to_thread(
        stripe.Subscription.retrieve, subscription_id
      )
      if hasattr(subscription, 'to_dict_recursive'):
        subscription = subscription.to_dict_recursive()
      (
        billing_frequency,
        billing_period,
        period_start,
        period_end,
      ) = _subscription_period(subscription)
    except (stripe.StripeError, TypeError, ValueError) as e:
      print(f'Unable to retrieve Stripe subscription details: {type(e).__name__}')
      return web.Response(status=503, text='Unable to retrieve subscription details')

    try:
      raw_amount = session.get('amount_total')
      amount = Decimal(raw_amount) / Decimal(100) if raw_amount is not None else None
      event_created = event.get('created')
      paid_at = (
        datetime.fromtimestamp(int(event_created), tz=UTC)
        if event_created is not None
        else datetime.now(UTC)
      )
      user_id = int(discord_user_id) if discord_user_id and discord_user_id.isdigit() else None
      guild_id = (
        int(discord_guild_id)
        if discord_guild_id and discord_guild_id.isdigit()
        else None
      )
      recorded = await RecordStripePayment(
        stripe_event_id=event.get('id', ''),
        stripe_checkout_session_id=session.get('id', ''),
        stripe_subscription_id=subscription_id,
        discord_id=guild_id,
        user_id=user_id,
        paid_at=paid_at,
        amount=amount,
        subscription_level=metadata.get('tier', 'Unknown'),
        billing_interval=billing_frequency,
        period_start=period_start,
        period_end=period_end,
      )
    except Exception as e:
      print(f'Failed to record Stripe payment: {type(e).__name__}')
      return web.Response(status=503, text='Unable to record payment')

    if not recorded:
      return web.Response(status=200, text='OK')

    confirmation = (
      f"Thank you for subscribing, **{discord_user_name}**!\n\n"
      f"Here's your confirmation:\n"
      f"> **Tier:** {tier}\n"
      f"> **Billing:** {billing_frequency}\n"
      f"> **Current period:** {billing_period}\n"
      f"> **Your Discord ID:** `{discord_user_id or 'Unknown'}`\n"
      f"> **Server ID:** `{discord_guild_id or 'Unknown'}`\n\n"
      f"If you have any questions, please reach out to the server owner."
    )

    if discord_user_id and discord_user_id.isdigit():
      try:
        user = await bot.fetch_user(int(discord_user_id))
        await user.send(confirmation)
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
