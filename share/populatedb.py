#   Author information
#   name: Vu Diep    
#   email: vdiep8@csu.fullerton.edu
#
#   This file
#   File name: populatedb.py
#   Purpose: populate the database with correct words and valids words

import sqlite3
import json

# Get the list of valid words
valid_f = open('share/valid.json')
VALID_DATA = json.load(valid_f)
valid_f.close()   

# Get the list of correct words and valid words and populate the database
correct_f = open('share/correct.json')
CORRECT_DATA = json.load(correct_f)
correct_f.close()

# Connect to db
connection = sqlite3.connect(f'./var/wordle.db')
cursor = connection.cursor()

# Create table
cursor.execute("DROP TABLE IF EXISTS valid")
cursor.execute("""
CREATE TABLE valid(
    word VARCHAR primary key
);
""")

cursor.execute("DROP TABLE IF EXISTS correct;")
cursor.execute("""
CREATE TABLE correct(
    word VARCHAR primary key
);
""")


# Loop Json files and insert
for i in range(0, len(VALID_DATA)):
    cursor.execute("INSERT INTO valid (word) VALUES(?)", (VALID_DATA[i],))

for i in range(0, len(CORRECT_DATA)):
    cursor.execute("INSERT INTO correct (word) VALUES(?)", (CORRECT_DATA[i],))

print('Database is populated with correct and valid words')
connection.commit()
connection.close()  