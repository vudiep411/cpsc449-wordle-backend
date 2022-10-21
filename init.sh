#!/bin/sh
# Initialize the database and populate with correct and 
# valid words from json
# Only do this when database is empty

rm ./var/wordle.db
sqlite3 ./var/wordle.db < ./share/wordle.sql
python3 populatedb.py
echo "Created database schema from worldle.sql"