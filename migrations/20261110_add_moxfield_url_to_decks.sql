ALTER TABLE public.decks
    ADD COLUMN IF NOT EXISTS moxfield_url TEXT;
