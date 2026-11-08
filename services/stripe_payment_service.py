import asyncio

import stripe
import settings


PAYMENT_CURRENCY = "usd"
PAYMENT_TIERS = {
    "player": {
        "amount": 500,
        "label": "$5.00/month",
        "name": "Player Monthly Subscription",
    },
    "store": {
        "amount": 1000,
        "label": "$10.00/month",
        "name": "Store Monthly Subscription",
    },
    "hub": {
        "amount": 2000,
        "label": "$20.00/month",
        "name": "Hub Monthly Subscription",
    },
}


async def create_subscription_session(
    *,
    tier: str,
    discord_user_id: int,
    discord_user_name: str,
    discord_guild_id: int | None,
):
    config = PAYMENT_TIERS.get(tier)
    if config is None:
        raise ValueError("Unknown subscription tier")
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("Stripe payments are not configured")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    metadata = {
        "discord_user_id": str(discord_user_id),
        "discord_user_name": discord_user_name,
        "discord_guild_id": str(discord_guild_id or ""),
        "tier": tier,
    }
    return await asyncio.to_thread(
        stripe.checkout.Session.create,
        line_items=[
            {
                "price_data": {
                    "currency": PAYMENT_CURRENCY,
                    "unit_amount": config["amount"],
                    "product_data": {"name": config["name"]},
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url="https://discord.com/channels/@me",
        cancel_url="https://discord.com/channels/@me",
        metadata=metadata,
        subscription_data={"metadata": metadata},
    )
