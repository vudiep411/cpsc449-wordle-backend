#   Author information
#   name: Vu Diep    
#   email: vdiep8@csu.fullerton.edu
#
#   This file
#   File name: queries.py
#   Purpose: Perform SQL queries

from random import randint
from quart import abort


# Add a new game for a user
# @Param 
# username -> str
# db -> database object
# return game_id -> int, created game's id
async def add_new_game(username, db):
    d = await db.fetch_all('SELECT word FROM correct')
    correctData = [item for t in d for item in t]
    randomIndex = randint(0, len(correctData) - 1)
    CORRECT_WORD = correctData[randomIndex]  
    game_id = await db.execute(
        """
        INSERT INTO game(username, correct_word, win, num_of_guesses) 
        VALUES(:username, :correct_word, :win, :num_of_guesses)
        """, 
        values={"username": username, "correct_word": CORRECT_WORD, "win": False, "num_of_guesses": 0})

    return game_id


# Fetch the secret correct word from a specific game session
# @Param
# username -> str
# id -> int, game_id
# db -> database object
# return correct_word[0] -> str, current game correct word
async def get_game_correct_word(username, id, db, app):
    correct_word = await db.fetch_one(
        'SELECT correct_word from game WHERE username=:username AND id=:id',
        values={"username": username, "id": id})
    app.logger.info('SELECT correct_word from game WHERE username=:username AND id=:id')
    return correct_word[0]    


# Add a user guessed word into the database
# username -> str
# guess_word -> str, user guessed word
# db -> database oject
async def add_user_guessed_word(id, username, guess_word, db):
    await db.execute(
        """
        INSERT INTO userInput(username, guess_word, game_id)
        VALUES(:username, :guess_word, :game_id)
        """,
        values={"username": username, "guess_word": guess_word, "game_id": id}
    )


# Set the game status win to True
# id -> int, game_id
# username -> str
async def set_win_user(id, username, db):
    await db.execute(
    """
    UPDATE game SET win=:win WHERE id=:id AND username=:username
    """, 
    values={"win": True, "id": id, "username": username})  


# increment user's guess by one
# id -> int, game id
# username -> str
async def increment_guesses(id, username, db):
    await db.execute(
        "UPDATE game SET num_of_guesses=num_of_guesses + 1 WHERE id=:id AND username=:username ",
        values={"id": id, "username" : username}
        )


# Fetch number of guesses from a game
# id -> int, game id
# username -> str
# return guesses -> tuple(num_of_guesses:int)
async def get_game_num_guesses(id, username, db, app):
    guesses = await db.fetch_one(
        "SELECT num_of_guesses FROM game WHERE id=:id AND username=:username",
        values={"id": id, "username": username}
    )
    app.logger.info("SELECT num_of_guesses FROM game WHERE id=:id AND username=:username")
    return guesses    


# Get win or lose for a specific game session in db
# id -> int, game id
# username -> str
# return won -> tuple(win:bool)
async def get_win_query(id, username, db, app):
    won = await db.fetch_one(
        'SELECT win FROM game WHERE username=:username AND id=:id',
        values={"username": username, "id": id}
    )
    app.logger.info('SELECT win FROM game WHERE username=:username AND id=:id')
    return won


# Get all guessword from a specific user from a specific game
# game_id -> int, game's id
# username -> str
# db -> database object
async def get_guesswords_in_game(game_id, username, db, app):
    game_guess_words = await db.fetch_all(
        'SELECT guess_word FROM userInput WHERE game_id=:game_id AND username=:username',
        values={"game_id": game_id, "username": username}
    )
    app.logger.info("SELECT guess_word FROM userInput WHERE game_id=:game_id AND username=:username")
    if game_guess_words:
        guessword_list = [item for t in game_guess_words for item in t]
        return guessword_list 
    return []


# Get a game by id
# game_id -> int
# username -> str
# db -> database object
async def get_game_by_id(game_id, username, db, app):
    game = await db.fetch_one(
        "SELECT id, username, win, num_of_guesses FROM game WHERE id = :id AND username=:username", 
        values={"id": game_id, "username": username}
    )

    app.logger.info("SELECT id, username, win, num_of_guesses FROM game WHERE id = :id AND username=:username")

    if game:
        return dict(game)
    return {}
