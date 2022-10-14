-- Database People please
-- Create the database here
-- When finish creating database run the command below at the root folder
-- $ sqlite3 ./var/wordle.db < ./share/wordle.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

-- Example table modify to meet the project requirements
--  *******************CREATE YOUR SCHEMA HERE *******************
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER primary key,
    username VARCHAR,
    password VARCHAR,       
    UNIQUE(username)
);

INSERT INTO users(username, password) VALUES('vudiep411', 'vudiep411');
COMMIT;