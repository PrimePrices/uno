CREATE TABLE IF NOT EXISTS facts(
    id UNIQUE AUTOINCREMENT,
    date_written DATE,
    fact TEXT,
    sources TEXT,
    tags TEXT,
    sponsor TEXT,
    views INTEGER
);
CREATE TABLE IF NOT EXISTS tags(
    id UNIQUE INT AUTOINCREMENT,
    tag TEXT,
    number_of_facts INT,
    list_of_facts TEXT
)