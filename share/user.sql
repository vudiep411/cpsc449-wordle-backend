PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    username VARCHAR,
    password VARCHAR,      
    UNIQUE(username)
);

COMMIT;