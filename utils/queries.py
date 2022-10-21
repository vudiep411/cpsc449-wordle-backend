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
# user_id -> int, user_id
# db -> database object
# return game_id -> int, created game's id
async def add_new_game(user_id, db):
    d = await db.fetch_all('SELECT word FROM correct')
    correctData = [item for t in d for item in t]
    randomIndex = randint(0, len(correctData) - 1)
    CORRECT_WORD = correctData[randomIndex]  
    game_id = await db.execute(
        """
        INSERT INTO game(user_id, correct_word, win, num_of_guesses) 
        VALUES(:user_id, :correct_word, :win, :num_of_guesses)
        """, 
        values={"user_id": user_id, "correct_word": CORRECT_WORD, "win": False, "num_of_guesses": 0})

    return game_id


# Fetch the secret correct word from a specific game session
# @Param
# user_id -> int, user_id
# id -> int, game_id
# db -> database object
# return correct_word[0] -> str, current game correct word
async def get_game_correct_word(user_id, id, db):
    correct_word = await db.fetch_one(
        'SELECT correct_word from game WHERE user_id=:user_id AND id=:id',
        values={"user_id": user_id, "id": id})
    return correct_word[0]    


# Return single user for testing purpose 
# id -> user_id
# db -> database oject
async def get_one_user(id, db):
    user = await db.fetch_one("SELECT * FROM users WHERE id = :id", values={"id": id})
    if user:
        return dict(user)
    else:
        abort(404)


# Add a user guessed word into the database
# user_id -> int, user_id
# guess_word -> str, user guessed word
# db -> database oject
async def add_user_guessed_word(id, user_id, guess_word, db):
    await db.execute(
        """
        INSERT INTO userInput(user_id, guess_word, game_id)
        VALUES(:user_id, :guess_word, :game_id)
        """,
        values={"user_id": user_id, "guess_word": guess_word, "game_id": id}
    )


# Set the game status win to True
# id -> int, game_id
# user_id -> int, user_id
async def set_win_user(id, user_id, db):
    await db.execute(
    """
    UPDATE game SET win=:win WHERE id=:id AND user_id=:user_id
    """, 
    values={"win": True, "id": id, "user_id": user_id})  


# increment user's guess by one
# id -> int, game id
# user_id -> int, user id
async def increment_guesses(id, user_id, db):
    await db.execute(
        "UPDATE game SET num_of_guesses=num_of_guesses + 1 WHERE id=:id AND user_id=:user_id ",
        values={"id": id, "user_id" : user_id}
        )


# Fetch number of guesses from a game
# id -> int, game id
# user_id -> int, user id
# return guesses -> tuple(num_of_guesses:int)
async def get_game_num_guesses(id, user_id, db):
    guesses = await db.fetch_one(
        "SELECT num_of_guesses FROM game WHERE id=:id AND user_id=:user_id",
        values={"id": id, "user_id": user_id}
    )
    return guesses    


# Get win or lose for a specific game session in db
# id -> int, game id
# user_id -> int, user id
# return won -> tuple(win:bool)
async def get_win_query(id, user_id, db):
    won = await db.fetch_one(
        'SELECT win FROM game WHERE user_id=:user_id AND id=:id',
        values={"user_id": user_id, "id": id}
    )
    return won


# Register a user in database
# username -> str, username from request data
# password -> str, password from request data
# return user_id -> int, newly created user's id
async def add_user(username, password, db):
    user_id = await db.execute(
        """
        INSERT INTO users(username, password)
        VALUES(:username, :password)
        """,
        values={
            "username": username, 
            "password": password
        },
        )
    return user_id


# Get user by username
# username -> str, username from request data
# return tuple(id:int, username:str, password:str)
async def get_user_by_username(username, db):
    user = await db.fetch_one("SELECT * from users WHERE username=:username",
    values={"username": username}
    )
    return user


# Get all guessword from a specific user from a specific game
# game_id -> int, game's id
# user_id -> int, user's id
# db -> database object
async def get_guesswords_in_game(game_id, user_id, db):
    game_guess_words = await db.fetch_all(
        'SELECT guess_word FROM userInput WHERE game_id=:game_id AND user_id=:user_id',
        values={"game_id": game_id, "user_id": user_id}
    )
    if game_guess_words:
        guessword_list = [item for t in game_guess_words for item in t]
        return guessword_list 
    return []


# Get a game by id
# game_id -> int
# user_id -> int
# db -> database object
async def get_game_by_id(game_id, user_id, db):
    game = await db.fetch_one(
        "SELECT * FROM game WHERE id = :id AND user_id=:user_id", 
        values={"id": game_id, "user_id": user_id}
    )
    if game:
        return dict(game)
    return {}
