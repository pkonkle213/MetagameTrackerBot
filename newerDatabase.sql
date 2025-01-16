DROP TABLE IF EXISTS NewStores;
CREATE TABLE NewStores (
  discord_id INTEGER PRIMARY KEY,
  discord_name TEXT,
  store_name TEXT,
  owner_id INTEGER,
  owner_name TEXT,
  isApproved BOOLEAN
);

DROP TABLE IF EXISTS NewCardGames;
CREATE TABLE NewCardGames (
  id SERIAL PRIMARY KEY,
  name TEXT
);

DROP TABLE IF EXISTS NewFormats;
CREATE TABLE NewFormats (
  id SERIAL PRIMARY KEY,
  game_id INTEGER REFERENCES NewCardGames (id),
  name TEXT
);

DROP TABLE IF EXISTS NewGameNameMaps;
CREATE TABLE NewGameNameMaps (
  game_id INTEGER REFERENCES NewCardGames (id),
  discord_id INTEGER REFERENCES NewStores (discord_id),
  used_name TEXT,
  PRIMARY KEY (game_id, discord_id)
);

DROP TABLE IF EXISTS NewEvents;
Create table NewEvents (
  id SERIAL PRIMARY KEY,
  discord_id INTEGER,
  store_name TEXT,
  user_id INTEGER,
  event_date date NOT NULL,
  game_id INTEGER,
  format_id INTEGER,
  event_type_id INTEGER,
  deck_played TEXT
);

DROP TABLE IF EXISTS NewParticipants;
CREATE TABLE NewParticipants (
  id SERIAL PRIMARY KEY,
  event_id INTEGER REFERENCES NewEvents (id),
  player_name TEXT,
  archetype_played TEXT,
  wins INTEGER,
  losses INTEGER,
  ties INTEGER,
  submitter_id INTEGER,
  UNIQUE(event_id, player_name)
);

DROP TABLE IF EXISTS NewInputTracker;
CREATE TABLE NewInputTracker (
  id SERIAL PRIMARY KEY,
  user_name TEXT,
  user_id INTEGER,
  archetype_played TEXT,
  date_submitted DATE,
  player_name TEXT,
  discord_id INTEGER REFERENCES NewStores (discord_id),
);


--Idea for tagging those who have submitted their deck
--SELECT user_id
--FROM inputtracker
--WHERE user_id IN %s
--GROUP BY player_name, user_id
--%s being an object passed in that's a list of people's names from Companion