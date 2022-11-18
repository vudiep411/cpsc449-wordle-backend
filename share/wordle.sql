-- When finish creating database run the command below at the root folder
-- $ sqlite3 ./var/wordle.db < ./share/wordle.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;


--  *******************CREATE YOUR SCHEMA HERE *******************
DROP TABLE IF EXISTS game;
CREATE TABLE game(
    id INTEGER primary key,
    user_id,
    correct_word VARCHAR,
    win BOOLEAN,
    num_of_guesses INT      
);

CREATE INDEX game_idx_1
ON game (user_id, num_of_guesses);

CREATE INDEX game_idx_2
ON game (user_id, id);

DROP TABLE IF EXISTS userInput;
CREATE TABLE userInput(
    id INTEGER primary key,
    user_id,
    game_id INT references game(id),
    guess_word VARCHAR
);

CREATE INDEX userInput_idx_1
ON userInput (user_id, game_id);
COMMIT;