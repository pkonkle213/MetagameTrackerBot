import stripe
import discord
from aiohttp import web
import settings


async def handle_stripe_webhook(request: web.Request, bot: discord.Client) -> web.Response:
  payload = await request.read()
  sig_header = request.headers.get('Stripe-Signature', '')

  if not settings.STRIPE_WEBHOOK_SECRET:
    print('Stripe webhook secret not configured')
    return web.Response(status=400, text='Webhook secret not configured')

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
  except stripe.errors.SignatureVerificationError:
    print('Invalid Stripe webhook signature')
    return web.Response(status=400, text='Invalid signature')
  except Exception as e:
    print(f'Webhook error: {e}')
    return web.Response(status=400, text=str(e))

  if event['type'] == 'checkout.session.completed':
    session = event['data']['object']
    metadata = session.get('metadata', {})

    discord_user_id = metadata.get('discord_user_id')
    discord_guild_id = metadata.get('discord_guild_id')
    discord_user_name = metadata.get('discord_user_name', 'Unknown')
    tier = metadata.get('tier', 'Unknown').title()

    print(f'Payment completed: user={discord_user_id}, guild={discord_guild_id}, tier={tier}')

    if discord_user_id:
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
        print(f'Failed to DM user {discord_user_id}: {e}')

  return web.Response(status=200, text='OK')


async def start_webhook_server(bot: discord.Client) -> None:
  stripe.api_key = settings.STRIPE_SECRET_KEY

  app = web.Application()
  app.router.add_post('/stripe/webhook', lambda req: handle_stripe_webhook(req, bot))

  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', 8080)
  await site.start()
  print('Stripe webhook server listening on port 8080')
