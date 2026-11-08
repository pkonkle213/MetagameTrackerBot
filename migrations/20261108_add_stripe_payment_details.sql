ALTER TABLE public.payments
    ADD COLUMN IF NOT EXISTS stripe_event_id TEXT,
    ADD COLUMN IF NOT EXISTS stripe_checkout_session_id TEXT,
    ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT,
    ADD COLUMN IF NOT EXISTS subscription_level TEXT,
    ADD COLUMN IF NOT EXISTS billing_interval TEXT,
    ADD COLUMN IF NOT EXISTS period_start TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS period_end TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS payments_stripe_event_id_uq
    ON public.payments (stripe_event_id);
