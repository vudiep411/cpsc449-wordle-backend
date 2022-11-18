#!/bin/sh
# Initialize the database and populate with correct and 
# valid words from json
# Only do this when database is empty

rm ./var/wordle.db
rm ./var/user.db
sqlite3 ./var/wordle.db < ./share/wordle.sql
sqlite3 ./var/user.db < ./share/user.sql
python3 ./share/populatedb.py
echo "Created database schema from worldle.sql"