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

DROP TABLE IF EXISTS guess_result;
CREATE TABLE guess_result(
    id INTEGER primary key,
    correct_word VARCHAR    
);

DROP TABLE IF EXISTS userInput;
CREATE TABLE userInput(
    id INTEGER primary key,
    user_id INT references users(id),
    guess_word VARCHAR
);

INSERT INTO users(username, password) VALUES('vudiep411', 'vudiep411');
INSERT INTO users(username, password) VALUES('JiuLin', '123456');
INSERT INTO userInput(user_id, guess_word) VALUES(1, 'WITCH');
INSERT INTO userInput(user_id, guess_word) VALUES(2, 'BITCH');
INSERT INTO userInput(user_id, guess_word) VALUES(2, 'HELLO');
COMMIT;