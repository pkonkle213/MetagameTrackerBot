from psycopg import AsyncConnection

from settings import DATABASE_URL


async def RecordPayment(
    *,
    discord_id: int | None,
    user_id: int | None,
    amount: int | None,
    checkout_session_id: str,
    subscription_id: str | None,
    stripe_event_id: str,
) -> bool:
    """Record a checkout amount in Stripe's minor currency units.

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
                amount,
                checkout_session_id,
                subscription_id,
                stripe_event_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (stripe_event_id) DO NOTHING
            RETURNING stripe_event_id
            """,
            (
                discord_id,
                user_id,
                amount,
                checkout_session_id,
                subscription_id,
                stripe_event_id,
            ),
        )
        return await cur.fetchone() is not None
