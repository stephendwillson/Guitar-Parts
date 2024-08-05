CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    tuning TEXT,
    notes TEXT,
    album TEXT,
    duration TEXT,
    genres TEXT
);