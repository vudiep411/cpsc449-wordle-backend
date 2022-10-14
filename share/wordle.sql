-- $ sqlite3 ./var/wordle.db < ./share/wordle.sql
-- Create the database here

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

-- DROP TABLE IF EXISTS games;
-- CREATE TABLE games (

-- )


DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER primary key,
    username VARCHAR,
    password VARCHAR,       
    UNIQUE(username)
);

INSERT INTO users(username, password) VALUES('vudiep411', 'vudiep411');
COMMIT;