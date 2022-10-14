#!/bin/sh

# only do this when database is empty
sqlite3 ./var/wordle.db < ./share/wordle.sql
echo "Create database schema from ./share/worldle.sql"