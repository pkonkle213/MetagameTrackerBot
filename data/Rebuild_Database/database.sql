CREATE SCHEMA "public";
CREATE TABLE "archetypesubmissions" (
  "id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "archetypesubmissions_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "event_id" integer,
  "player_name" text,
  "archetype_played" text,
  "date_submitted" timestamp,
  "submitter_id" bigint,
  "submitter_username" text,
  "reported" boolean
);
CREATE TABLE "badwords" (
  "id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "badwords_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "badword" text
);
CREATE TABLE "badwords_stores" (
  "badword_id" integer,
  "discord_id" bigint,
  CONSTRAINT "badwords_stores_pk" PRIMARY KEY("badword_id","discord_id")
);
CREATE TABLE "claimchannels" (
  "discord_id" bigint,
  "channel_id" bigint,
  "game_id" bigint,
  CONSTRAINT "pk_claimreportchannels" PRIMARY KEY("discord_id","game_id")
);
CREATE TABLE "events" (
  "id" serial PRIMARY KEY,
  "discord_id" bigint CONSTRAINT "events_discord_id_key" UNIQUE,
  "event_date" date NOT NULL CONSTRAINT "events_event_date_key" UNIQUE,
  "game_id" integer CONSTRAINT "events_game_id_key" UNIQUE,
  "format_id" integer CONSTRAINT "events_format_id_key" UNIQUE,
  "last_update" smallint,
  "is_posted" boolean,
  "is_complete" boolean,
  CONSTRAINT "events_discord_id_event_date_game_id_format_id_key" UNIQUE("discord_id","event_date","game_id","format_id")
);
CREATE TABLE "formatchannelmaps" (
  "channel_id" bigint,
  "format_id" integer,
  "discord_id" bigint,
  CONSTRAINT "primary_key" PRIMARY KEY("channel_id","discord_id")
);
CREATE TABLE "formats" (
  "id" serial PRIMARY KEY,
  "game_id" integer CONSTRAINT "formats_game_id_key" UNIQUE,
  "name" text CONSTRAINT "formats_name_key" UNIQUE,
  "last_ban_update" date,
  "is_limited" boolean,
  CONSTRAINT "formats_game_id_name_key" UNIQUE("game_id","name")
);
CREATE TABLE "gamecategorymaps" (
  "game_id" integer,
  "discord_id" bigint,
  "category_id" bigint,
  CONSTRAINT "gamecategorymaps_pk" PRIMARY KEY("discord_id","category_id")
);
CREATE TABLE "games" (
  "id" serial,
  "name" text CONSTRAINT "cardgames_name_key" UNIQUE,
  CONSTRAINT "cardgames_pkey" PRIMARY KEY("id")
);
CREATE TABLE "individual_event_types" (
  "event_type_id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "individual_event_types_event_type_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "event_type_name" text
);
CREATE TABLE "individual_events" (
  "individual_event_id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "individual_events_individual_event_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "discord_user_id" bigint,
  "event_date" date,
  "event_type_id" integer,
  "player_archetype" text,
  "location_name" text,
  "game" text,
  "format" text
);
CREATE TABLE "individual_games" (
  "individual_game_id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "individual_games_individual_game_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "game_number" integer,
  "on_the_play" boolean,
  "player_mulligan" integer,
  "opponent_mulligan" integer,
  "game_result_id" integer,
  "individual_match_id" integer
);
CREATE TABLE "individual_matches" (
  "match_id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "individual_matches_match_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "event_id" integer,
  "opponent_name" text,
  "opponent_archetype" text,
  "result_type_id" integer,
  "won_choice" boolean
);
CREATE TABLE "individual_result_types" (
  "result_type_id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "individual_result_types_result_type_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
  "result_name" text
);
CREATE TABLE "individual_users" (
  "discord_user_id" bigint PRIMARY KEY,
  "name" text
);
CREATE TABLE "pairings" (
  "event_id" integer,
  "round_number" integer,
  "submitter_id" bigint,
  "player1_game_wins" integer,
  "player2_game_wins" integer,
  "player1_name" text,
  "player2_name" text,
  CONSTRAINT "rounddetails_primary_key" PRIMARY KEY("event_id","round_number","player2_name","player1_name")
);
CREATE TABLE "standings" (
  "id" serial,
  "event_id" integer CONSTRAINT "standings_event_id_key" UNIQUE,
  "player_name" text CONSTRAINT "standings_player_name_key" UNIQUE,
  "wins" integer,
  "losses" integer,
  "draws" integer,
  "submitter_id" bigint,
  CONSTRAINT "participants_pkey" PRIMARY KEY("id"),
  CONSTRAINT "participants_event_id_player_name_key" UNIQUE("event_id","player_name")
);
CREATE TABLE "stores" (
  "discord_id" bigint PRIMARY KEY,
  "discord_name" text,
  "store_name" text,
  "owner_id" bigint,
  "owner_name" text,
  "used_for_data" boolean,
  "last_payment" date,
  "state" text,
  "region" text,
  "melee_client_id" text,
  "melee_client_secret" text,
  "is_data_hub" boolean,
  "store_address" text
);
ALTER TABLE "archetypesubmissions" ADD CONSTRAINT "archetypes_event_id_fk" FOREIGN KEY ("event_id") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "claimchannels" ADD CONSTRAINT "fk_claimreportchannels_games" FOREIGN KEY ("game_id") REFERENCES "games"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "claimchannels" ADD CONSTRAINT "fk_claimreportchannels_stores" FOREIGN KEY ("discord_id") REFERENCES "stores"("discord_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "events" ADD CONSTRAINT "events_format_id_fkey" FOREIGN KEY ("format_id") REFERENCES "formats"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "events" ADD CONSTRAINT "events_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "games"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "events" ADD CONSTRAINT "events_stores_discord_id_fkey" FOREIGN KEY ("discord_id") REFERENCES "stores"("discord_id") ON DELETE SET DEFAULT ON UPDATE CASCADE;
ALTER TABLE "formatchannelmaps" ADD CONSTRAINT "formatchannelmaps_discord_id_fk" FOREIGN KEY ("discord_id") REFERENCES "stores"("discord_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "formatchannelmaps" ADD CONSTRAINT "formatchannelmaps_format_id_fk" FOREIGN KEY ("format_id") REFERENCES "formats"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "formats" ADD CONSTRAINT "formats_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "games"("id");
ALTER TABLE "gamecategorymaps" ADD CONSTRAINT "gamecategorymaps_discord_id_fk" FOREIGN KEY ("discord_id") REFERENCES "stores"("discord_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "gamecategorymaps" ADD CONSTRAINT "gamecategorymaps_game_id_fk" FOREIGN KEY ("game_id") REFERENCES "games"("id");
ALTER TABLE "individual_events" ADD CONSTRAINT "fk_events_types" FOREIGN KEY ("event_type_id") REFERENCES "individual_event_types"("event_type_id");
ALTER TABLE "individual_events" ADD CONSTRAINT "fk_events_users" FOREIGN KEY ("discord_user_id") REFERENCES "individual_users"("discord_user_id");
ALTER TABLE "individual_games" ADD CONSTRAINT "fk_games_matches" FOREIGN KEY ("individual_match_id") REFERENCES "individual_matches"("match_id");
ALTER TABLE "individual_games" ADD CONSTRAINT "fk_games_results" FOREIGN KEY ("game_result_id") REFERENCES "individual_result_types"("result_type_id");
ALTER TABLE "individual_matches" ADD CONSTRAINT "fk_matches_events" FOREIGN KEY ("event_id") REFERENCES "individual_events"("individual_event_id");
ALTER TABLE "individual_matches" ADD CONSTRAINT "fk_matches_results" FOREIGN KEY ("result_type_id") REFERENCES "individual_result_types"("result_type_id");
ALTER TABLE "pairings" ADD CONSTRAINT "rounddetails_events_event_id_fk" FOREIGN KEY ("event_id") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "standings" ADD CONSTRAINT "participants_event_id_fkey" FOREIGN KEY ("event_id") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;
CREATE UNIQUE INDEX "archetypesubmissions_pkey" ON "archetypesubmissions" ("id");
CREATE UNIQUE INDEX "badwords_pkey" ON "badwords" ("id");
CREATE UNIQUE INDEX "badwords_stores_pk" ON "badwords_stores" ("badword_id","discord_id");
CREATE UNIQUE INDEX "pk_claimreportchannels" ON "claimchannels" ("discord_id","game_id");
CREATE UNIQUE INDEX "events_discord_id_event_date_game_id_format_id_key" ON "events" ("discord_id","event_date","game_id","format_id");
CREATE UNIQUE INDEX "events_discord_id_key" ON "events" ("discord_id");
CREATE UNIQUE INDEX "events_event_date_key" ON "events" ("event_date");
CREATE UNIQUE INDEX "events_format_id_key" ON "events" ("format_id");
CREATE UNIQUE INDEX "events_game_id_key" ON "events" ("game_id");
CREATE UNIQUE INDEX "events_pkey" ON "events" ("id");
CREATE UNIQUE INDEX "primary_key" ON "formatchannelmaps" ("channel_id","discord_id");
CREATE UNIQUE INDEX "formats_game_id_key" ON "formats" ("game_id");
CREATE UNIQUE INDEX "formats_game_id_name_key" ON "formats" ("game_id","name");
CREATE UNIQUE INDEX "formats_name_key" ON "formats" ("name");
CREATE UNIQUE INDEX "formats_pkey" ON "formats" ("id");
CREATE UNIQUE INDEX "gamecategorymaps_pk" ON "gamecategorymaps" ("discord_id","category_id");
CREATE UNIQUE INDEX "cardgames_name_key" ON "games" ("name");
CREATE UNIQUE INDEX "cardgames_pkey" ON "games" ("id");
CREATE UNIQUE INDEX "individual_event_types_pkey" ON "individual_event_types" ("event_type_id");
CREATE UNIQUE INDEX "individual_events_pkey" ON "individual_events" ("individual_event_id");
CREATE UNIQUE INDEX "individual_games_pkey" ON "individual_games" ("individual_game_id");
CREATE UNIQUE INDEX "individual_matches_pkey" ON "individual_matches" ("match_id");
CREATE UNIQUE INDEX "individual_result_types_pkey" ON "individual_result_types" ("result_type_id");
CREATE UNIQUE INDEX "individual_users_pkey" ON "individual_users" ("discord_user_id");
CREATE UNIQUE INDEX "rounddetails_primary_key" ON "pairings" ("event_id","round_number","player2_name","player1_name");
CREATE UNIQUE INDEX "participants_event_id_player_name_key" ON "standings" ("event_id","player_name");
CREATE UNIQUE INDEX "participants_pkey" ON "standings" ("id");
CREATE UNIQUE INDEX "standings_event_id_key" ON "standings" ("event_id");
CREATE UNIQUE INDEX "standings_player_name_key" ON "standings" ("player_name");
CREATE UNIQUE INDEX "stores_pkey" ON "stores" ("discord_id");
CREATE VIEW "events_reported" AS (SELECT e.id, e.discord_id, count(*) FILTER (WHERE a.archetype_played IS NOT NULL) AS reported, count(*) AS total_attended, 1.0 * count(*) FILTER (WHERE a.archetype_played IS NOT NULL)::numeric / count(*)::numeric AS reported_percent FROM ( SELECT e_1.id, asu.archetype_played FROM events e_1 JOIN full_standings fp ON fp.event_id = e_1.id LEFT JOIN unique_archetypes asu ON asu.event_id = e_1.id AND upper(asu.player_name) = upper(fp.player_name) ORDER BY e_1.id DESC) a JOIN events e ON a.id = e.id JOIN stores s ON s.discord_id = e.discord_id WHERE s.used_for_data = true GROUP BY e.id ORDER BY e.event_date DESC);
CREATE VIEW "events_view" AS (SELECT e.id, e.discord_id, e.event_date, e.game_id, e.format_id, e.last_update, CASE WHEN count(p.round_number) > 0 THEN 'PAIRINGS'::text WHEN count(s.player_name) > 0 THEN 'STANDINGS'::text ELSE NULL::text END AS event_type, e.is_posted, e.is_complete FROM events e LEFT JOIN pairings p ON p.event_id = e.id LEFT JOIN standings s ON s.event_id = e.id GROUP BY e.id);
CREATE VIEW "full_pairings" AS (SELECT pairings.event_id, pairings.round_number, pairings.player1_name AS player_name, pairings.player2_name AS opponent_name, CASE WHEN pairings.player1_game_wins > pairings.player2_game_wins THEN 'WIN'::text WHEN pairings.player1_game_wins = pairings.player2_game_wins THEN 'DRAW'::text ELSE 'LOSS'::text END AS result FROM pairings UNION SELECT rd.event_id, rd.round_number, rd.player2_name AS player_name, rd.player1_name AS opponent_name, CASE WHEN rd.player2_game_wins > rd.player1_game_wins THEN 'WIN'::text WHEN rd.player2_game_wins = rd.player1_game_wins THEN 'DRAW'::text ELSE 'LOSS'::text END AS result FROM pairings rd WHERE upper(rd.player2_name) <> 'BYE'::text ORDER BY 1 DESC, 2, 3);
CREATE VIEW "full_standings" AS (SELECT standings.event_id, standings.player_name, standings.wins, standings.losses, standings.draws FROM standings UNION ALL SELECT unnamed_subquery.event_id, upper(unnamed_subquery.player_name) AS player_name, sum(unnamed_subquery.wins) AS wins, sum(unnamed_subquery.losses) AS losses, sum(unnamed_subquery.draws) AS draws FROM ( SELECT pairings.event_id, pairings.player1_name AS player_name, CASE WHEN pairings.player1_game_wins > pairings.player2_game_wins THEN 1 ELSE 0 END AS wins, CASE WHEN pairings.player1_game_wins < pairings.player2_game_wins THEN 1 ELSE 0 END AS losses, CASE WHEN pairings.player1_game_wins = pairings.player2_game_wins THEN 1 ELSE 0 END AS draws FROM pairings UNION ALL SELECT pairings.event_id, pairings.player2_name AS player_name, CASE WHEN pairings.player2_game_wins > pairings.player1_game_wins THEN 1 ELSE 0 END AS wins, CASE WHEN pairings.player2_game_wins < pairings.player1_game_wins THEN 1 ELSE 0 END AS losses, CASE WHEN pairings.player2_game_wins = pairings.player1_game_wins THEN 1 ELSE 0 END AS draws FROM pairings WHERE upper(pairings.player2_name) <> 'BYE'::text) unnamed_subquery GROUP BY unnamed_subquery.event_id, (upper(unnamed_subquery.player_name)));
CREATE VIEW "player_names" AS (SELECT DISTINCT ON (e.discord_id, asu.submitter_id) asu.submitter_id, e.discord_id, upper(asu.player_name) AS player_name FROM archetypesubmissions asu JOIN events e ON e.id = asu.event_id WHERE asu.reported = false AND asu.submitter_id IS NOT NULL GROUP BY asu.submitter_id, e.discord_id, (upper(asu.player_name)) ORDER BY e.discord_id, asu.submitter_id, (count(*)) DESC);
CREATE VIEW "stores_view" AS (SELECT discord_id, discord_name, store_name, owner_id, owner_name, store_address, used_for_data, state, region, CASE WHEN last_payment >= (CURRENT_DATE - '1 mon'::interval) THEN true ELSE false END AS ispaid, COALESCE(is_data_hub, false) AS is_data_hub FROM stores);
CREATE VIEW "unique_archetypes" AS (SELECT DISTINCT ON (event_id, player_name) event_id, player_name, archetype_played, date_submitted, submitter_id, submitter_username, reported FROM archetypesubmissions WHERE reported = false ORDER BY event_id, player_name, id DESC);
CREATE VIEW "unknown_archetypes" AS (SELECT e.event_date, e.game_id, e.format_id, e.discord_id, p.player_name FROM ( SELECT p_1.event_id, p_1.player_name FROM standings p_1 UNION SELECT pairings.event_id, pairings.player1_name AS player_name FROM pairings UNION SELECT pairings.event_id, pairings.player2_name AS player_name FROM pairings WHERE upper(pairings.player2_name) <> 'BYE'::text) p JOIN events e ON p.event_id = e.id LEFT JOIN ( SELECT DISTINCT ON (archetypesubmissions.event_id, archetypesubmissions.player_name) archetypesubmissions.event_id, archetypesubmissions.player_name, archetypesubmissions.archetype_played, archetypesubmissions.submitter_id FROM archetypesubmissions WHERE archetypesubmissions.reported = false ORDER BY archetypesubmissions.event_id, archetypesubmissions.player_name, archetypesubmissions.id DESC) ap ON p.event_id = ap.event_id AND upper(p.player_name) = upper(ap.player_name) WHERE ap.archetype_played IS NULL ORDER BY e.event_date DESC, p.player_name);