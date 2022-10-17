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

DROP TABLE IF EXISTS game;
CREATE TABLE game(
    id INTEGER primary key,
    user_id INT references user(id),
    correct_word VARCHAR,
    win BOOLEAN,
    num_of_guesses INT      
);

DROP TABLE IF EXISTS userInput;
CREATE TABLE userInput(
    id INTEGER primary key,
    user_id INT references users(id),
    guess_word VARCHAR
);


COMMIT;