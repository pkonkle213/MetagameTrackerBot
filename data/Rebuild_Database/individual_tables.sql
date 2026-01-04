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
ALTER TABLE "individual_events" ADD CONSTRAINT "fk_events_types" FOREIGN KEY ("event_type_id") REFERENCES "individual_event_types"("event_type_id");
ALTER TABLE "individual_events" ADD CONSTRAINT "fk_events_users" FOREIGN KEY ("discord_user_id") REFERENCES "individual_users"("discord_user_id");
ALTER TABLE "individual_games" ADD CONSTRAINT "fk_games_matches" FOREIGN KEY ("individual_match_id") REFERENCES "individual_matches"("match_id");
ALTER TABLE "individual_games" ADD CONSTRAINT "fk_games_results" FOREIGN KEY ("game_result_id") REFERENCES "individual_result_types"("result_type_id");
ALTER TABLE "individual_matches" ADD CONSTRAINT "fk_matches_events" FOREIGN KEY ("event_id") REFERENCES "individual_events"("individual_event_id");
ALTER TABLE "individual_matches" ADD CONSTRAINT "fk_matches_results" FOREIGN KEY ("result_type_id") REFERENCES "individual_result_types"("result_type_id");
