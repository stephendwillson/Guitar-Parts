CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS songs (
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    tuning TEXT,
    notes TEXT,
    album TEXT,
    duration INTEGER,
    genres TEXT,
    progress TEXT DEFAULT 'Not Started',
    PRIMARY KEY (title, artist)
);