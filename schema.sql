-- CONFIGURATION SQLITE

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

PRAGMA foreign_keys = ON;



-- TABLES

CREATE TABLE IF NOT EXISTS song (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vote (
    better_id INTEGER NOT NULL,
    worse_id  INTEGER NOT NULL,

    PRIMARY KEY (better_id, worse_id),

    FOREIGN KEY (better_id) REFERENCES song(id) ON DELETE CASCADE,
    FOREIGN KEY (worse_id)  REFERENCES song(id) ON DELETE CASCADE,

    CHECK (better_id != worse_id)
);



-- INDEX

-- Pour compter rapidement les downvotes
CREATE INDEX IF NOT EXISTS idx_vote_better
ON vote(better_id);

-- Pour compter rapidement les upvotes
CREATE INDEX IF NOT EXISTS idx_vote_worse
ON vote(worse_id);



-- TRIGGER

-- Pour éviter les votes dans les deux sens
CREATE TRIGGER IF NOT EXISTS trg_vote_no_inverse
BEFORE INSERT ON vote
FOR EACH ROW
BEGIN
    DELETE FROM vote
    WHERE better_id = NEW.worse_id
      AND worse_id  = NEW.better_id;
END;



-- INSERT

