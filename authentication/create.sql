CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  salt TEXT,
  logged_in INTEGER,
  game_id TEXT
)