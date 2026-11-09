from datetime import datetime
from decimal import Decimal

from psycopg import AsyncConnection

from settings import DATABASE_URL


async def RecordPayment(
    *,
    discord_id: int | None,
    user_id: int | None,
    payment_date: datetime | None,
    amount: Decimal | None,
    checkout_session_id: str,
    subscription_id: str | None,
    subscription_level: str | None,
    billing_interval: str | None,
    stripe_event_id: str,
) -> bool:
    """Record a paid checkout using the public.payments schema.

    Return False when the Stripe event was already saved.
    """
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        await cur.execute(
            """
            INSERT INTO public.payments (
                discord_id,
                user_id,
                "date",
                amount,
                stripe_checkout_session_id,
                stripe_subscription_id,
                stripe_event_id,
                subscription_level,
                billing_interval
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stripe_event_id) DO NOTHING
            RETURNING stripe_event_id
            """,
            (
                discord_id,
                user_id,
                payment_date,
                amount,
                checkout_session_id,
                subscription_id,
                stripe_event_id,
                subscription_level,
                billing_interval,
            ),
        )
        return await cur.fetchone() is not None
