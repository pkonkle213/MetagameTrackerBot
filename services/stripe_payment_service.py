import asyncio

import stripe
import settings


PAYMENT_CURRENCY = "usd"
PAYMENT_TIERS = {
    "player": {
        "monthly": {
            "amount": 500,
            "label": "$5.00/month",
            "name": "Player Monthly Subscription",
            "interval": "month",
        },
        "yearly": {
            "amount": 5000,
            "label": "$50.00/year",
            "name": "Player Yearly Subscription",
            "interval": "year",
        },
    },
    "store": {
        "monthly": {
            "amount": 1000,
            "label": "$10.00/month",
            "name": "Store Monthly Subscription",
            "interval": "month",
        },
        "yearly": {
            "amount": 10000,
            "label": "$100.00/year",
            "name": "Store Yearly Subscription",
            "interval": "year",
        },
    },
}


async def create_subscription_session(
    *,
    tier: str,
    billing_interval: str,
    discord_user_id: int,
    discord_user_name: str,
    discord_guild_id: int | None,
):
    config = PAYMENT_TIERS.get(tier, {}).get(billing_interval)
    if config is None:
        raise ValueError("Unknown subscription tier or billing interval")
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("Stripe payments are not configured")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    metadata = {
        "discord_user_id": str(discord_user_id),
        "discord_user_name": discord_user_name,
        "discord_guild_id": str(discord_guild_id or ""),
        "tier": tier,
        "billing_period": billing_period,
    }
    return await asyncio.to_thread(
        stripe.checkout.Session.create,
        line_items=[
            {
                "price_data": {
                    "currency": PAYMENT_CURRENCY,
                    "unit_amount": config["amount"],
                    "product_data": {"name": config["name"]},
                    "recurring": {"interval": config["interval"]},
                },
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url="https://discord.com/channels/@me",
        cancel_url="https://discord.com/channels/@me",
        metadata={
            "discord_user_id": str(discord_user_id),
            "discord_user_name": discord_user_name,
            "discord_guild_id": str(discord_guild_id or ""),
            "tier": tier,
            "billing_interval": config["interval"],
        },
    )
