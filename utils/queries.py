import json
from random import randint
from quart import abort


# Add a new game for a user
# @Param 
# user_id -> user_id
# db -> database object
async def add_new_game(user_id, db):
    f = open('correct.json')
    correctData = json.load(f)
    randomIndex = randint(0, len(correctData) - 1)
    CORRECT_WORD = correctData[randomIndex]  
    game_id = await db.execute(
        """
        INSERT INTO game(user_id, correct_word, win, num_of_guesses) 
        VALUES(:user_id, :correct_word, :win, :num_of_guesses)
        """, 
        values={"user_id": user_id, "correct_word": CORRECT_WORD, "win": False, "num_of_guesses": 0})
    f.close()
    return game_id


# Fetch the secret correct word from a specific game session
# @Param
# user_id -> user_id
# id -> game_id
# db -> database object
async def get_correct_word_user(user_id, id, db):
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
# user_id -> user_id
# guess_word -> user guessed word
# db -> database oject
async def add_guessed_word(user_id, guess_word, db):
    await db.execute(
        """
        INSERT INTO userInput(user_id, guess_word)
        VALUES(:user_id, :guess_word)
        """,
        values={"user_id": user_id, "guess_word": guess_word}
    )


# Set the game status win to True
# id -> game_id
# user_id -> user_id
async def set_win_user(id, user_id, db):
    await db.execute(
    """
    UPDATE game SET win=:win WHERE id=:id AND user_id=:user_id
    """, 
    values={"win": True, "id": id, "user_id": user_id})  

# increment user's guess by one
async def increment_guesses(id, user_id, db):
    await db.execute(
        "UPDATE game SET num_of_guesses=num_of_guesses + 1 WHERE id=:id AND user_id=:user_id ",
        values={"id": id, "user_id" : user_id}
        )

# Fetch number of guesses from a game
async def get_game_guesses(id, user_id, db):
    guesses = await db.fetch_one(
        "SELECT num_of_guesses FROM game WHERE id=:id AND user_id=:user_id",
        values={"id": id, "user_id": user_id}
    )
    return guesses    

# Get win or lose for a specific game session in db
async def get_win(id, user_id, db):
    won = await db.fetch_one(
        'SELECT win FROM game WHERE user_id=:user_id AND id=:id',
        values={"user_id": user_id, "id": id}
    )
    return won

# Register a user in database
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