CREATE TABLE
    IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        owner_id INTEGER,
        name TEXT
    )
