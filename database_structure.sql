DROP TABLE IF EXISTS Stores;
CREATE TABLE Stores (
  discord_id BIGINT PRIMARY KEY,
  discord_name TEXT,
  store_name TEXT,
  owner_id BIGINT,
  owner_name TEXT,
  isApproved BOOLEAN
);

DROP TABLE IF EXISTS CardGames;
CREATE TABLE CardGames (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE,
  hasFormats BOOLEAN
);

DROP TABLE IF EXISTS Formats;
CREATE TABLE Formats (
  id SERIAL PRIMARY KEY,
  game_id INTEGER REFERENCES CardGames (id) ON DELETE CASCADE,
  name TEXT,
  UNIQUE (game_id, name)
);

DROP TABLE IF EXISTS GameNameMaps;
CREATE TABLE GameNameMaps (
  discord_id BIGINT REFERENCES Stores (discord_id) ON DELETE CASCADE,
  game_id INTEGER REFERENCES CardGames (id) ON DELETE CASCADE,
  used_name TEXT,
  PRIMARY KEY (game_id, discord_id)
);

DROP TABLE IF EXISTS Events;
Create table Events (
  id SERIAL PRIMARY KEY,
  discord_id BIGINT,
  event_date date NOT NULL,
  game_id INTEGER REFERENCES CardGames (id) ON DELETE CASCADE,
  format_id INTEGER REFERENCES Formats (id) ON DELETE CASCADE,
  UNIQUE (discord_id, event_date, game_id, format_id)
);

DROP TABLE IF EXISTS Participants;
CREATE TABLE Participants (
  id SERIAL PRIMARY KEY,
  event_id INTEGER REFERENCES Events (id) ON DELETE CASCADE,
  player_name TEXT,
  archetype_played TEXT,
  wins INTEGER,
  losses INTEGER,
  draws INTEGER,
  submitter_id BIGINT,
  UNIQUE(event_id, player_name)
);

DROP TABLE IF EXISTS InputTracker;
CREATE TABLE InputTracker (
  id SERIAL PRIMARY KEY,
  user_name TEXT,
  user_id BIGINT,
  archetype_played TEXT,
  date_submitted DATE,
  player_name TEXT,
  discord_id BIGINT REFERENCES Stores (discord_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS RoundDetails;
CREATE TABLE RoundDetails (
  id SERIAL PRIMARY KEY,
  event_id INTEGER REFERENCES Events (id) ON DELETE CASCADE,
  round_number INTEGER,
  player1_name TEXT,
  player1_wins INTEGER,
  player2_name TEXT,
  player2_wins INTEGER,
  UNQIUE (event_id, round_number, player1_name, player2_name)
);


--Idea for tagging those who have submitted their deck
--SELECT user_id
--FROM inputtracker
--WHERE user_id IN %s
--GROUP BY player_name, user_id
--%s being an object passed in that's a list of people's names from Companion