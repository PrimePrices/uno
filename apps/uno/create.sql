CREATE TABLE IF NOT EXISTS hands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  position INTEGER,
  game_id INTEGER,
  cards TEXT,
  username TEXT,
  number_of_cards INT DEFAULT 7
);
CREATE TABLE IF NOT EXISTS games(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rules TEXT DEFAULT "",
  number_of_players INTEGER DEFAULT 1,
  players TEXT,
  next_player TEXT,
  direction INTEGER DEFAULT 0, 
  discard TEXT,
  draw TEXT, 
  last_activity TEXT
)