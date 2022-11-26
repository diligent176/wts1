
-- WTS APP





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
