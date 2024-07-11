CREATE TABLE IF NOT EXISTS hands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    position INTEGER,
    cards TEXT,
    username TEXT,
    number_of_cards INT DEFAULT 7,
    request_sid TEXT,
    FOREIGN KEY (username) REFERENCES user(username),
    FOREIGN KEY (game_id)  REFERENCES games(id)
);
CREATE TABLE IF NOT EXISTS games(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rules TEXT DEFAULT "",
    number_of_players INTEGER DEFAULT 1,
    next_player INTEGER,
    direction INTEGER DEFAULT 0, 
    discard TEXT,
    draw TEXT, 
    last_activity TEXT,
    FOREIGN KEY (next_player) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    email TEXT,
    logged_in BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS super_user(
    id INTEGER,
    FOREIGN KEY (id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS facts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_written INTEGER,
    month_written INTEGER,
    day_written INTEGER,
    released BOOLEAN DEFAULT FALSE,
    fact TEXT,
    sources TEXT,
    sponsor TEXT,
    views INTEGER
);

CREATE TABLE IF NOT EXISTS tags_facts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT,
    fact_id INTEGER,
    FOREIGN KEY (fact_id) REFERENCES facts(id)
)