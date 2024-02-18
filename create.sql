CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  salt TEXT,
  logged_in INTEGER,
  game_id TEXT
);
CREATE TABLE IF NOT EXISTS hands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  position INTEGER,
  game_id INTEGER,
  cards TEXT,
  username INTEGER,
  number_of_cards INT
);
CREATE TABLE IF NOT EXISTS games(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rules TEXT,
  number_of_players INTEGER,
  players TEXT,
  next_player TEXT,
  direction INTEGER,
  discard TEXT,
  draw TEXT
)