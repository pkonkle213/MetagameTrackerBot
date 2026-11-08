from datetime import UTC, datetime
from decimal import Decimal

from psycopg import AsyncConnection

from settings import DATABASE_URL


async def RecordStripePayment(
    *,
    stripe_event_id: str,
    stripe_checkout_session_id: str,
    stripe_subscription_id: str,
    discord_id: int | None,
    user_id: int | None,
    paid_at: datetime,
    amount: Decimal | None,
    subscription_level: str,
    billing_interval: str,
    period_start: datetime,
    period_end: datetime,
) -> bool:
    """Record a completed Stripe subscription payment once per webhook event."""
    payment_date = paid_at.astimezone(UTC).replace(tzinfo=None)
    async with await AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO payments (
                    discord_id,
                    date,
                    amount,
                    user_id,
                    stripe_event_id,
                    stripe_checkout_session_id,
                    stripe_subscription_id,
                    subscription_level,
                    billing_interval,
                    period_start,
                    period_end
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stripe_event_id) DO NOTHING
                RETURNING id
                """,
                (
                    discord_id,
                    payment_date,
                    amount,
                    user_id,
                    stripe_event_id,
                    stripe_checkout_session_id,
                    stripe_subscription_id,
                    subscription_level,
                    billing_interval,
                    period_start,
                    period_end,
                ),
            )
            inserted = await cur.fetchone()
        await conn.commit()
    return inserted is not None
