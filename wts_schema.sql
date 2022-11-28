
-- WTS APP
-- CREATE a new database simply by opening in "sqlite3 newdb.db"
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    display_name TEXT,
    email TEXT,
    country TEXT,
    spotify_uri TEXT NOT NULL,
    spotify_url TEXT,
    visited_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

-- DROP TABLE users;
-- ALTER TABLE users ADD COLUMN spotify_url TEXT;
-- ALTER TABLE users RENAME COLUMN fullname TO display_name;

CREATE INDEX spotify_uri ON users (spotify_uri);
CREATE INDEX email ON users (email);


CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    track_name TEXT,
    track_artist TEXT,
    track_album TEXT,
    track_uri TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
    );

CREATE INDEX user_id ON tracks (user_id);

CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    points INTEGER,
    streak INTEGER,
    session_date TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
    );

CREATE INDEX scores_user_id ON scores (user_id);

-- TEST DATA
INSERT INTO users (fullname, email, country, spotify_uri) VALUES ("Dummy Dumdum", "salt@peppa.ca", "CA", "22heggrg45538jj2jj28");
INSERT INTO tracks (user_id, track_name, track_artist, track_album, track_uri) VALUES (1, "Love me do", "salt n peppa", "Hashy", "spotify:track:22heggrg45538jj2jj28");
INSERT INTO scores (user_id, points, streak, session_date) VALUES (1, 80, 12, "2022-11-27");


-- TESTING in new db wts.db
CREATE TABLE usr_tmp (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, spotid TEXT NOT NULL);
INSERT INTO usr_tmp (username, hash, spotid) VALUES ("billy", "salt n peppa", "22heggrg45538jj2jj28");

-- FINANCE APP
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00
);

CREATE TABLE sqlite_sequence(name,seq);

CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE shares (
    share_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX user_id ON shares (user_id);
CREATE INDEX symbol ON shares (symbol);
CREATE UNIQUE INDEX user_symbol ON shares (user_id, symbol);    -- enforce the unique user + symbol combination


CREATE TABLE transactions (
    txn_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX txn_user_id ON transactions (user_id);
