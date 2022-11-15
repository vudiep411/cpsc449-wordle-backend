# 449 Back-end Project-01  10/22/2022
# Team members:
# Vu Diep

import dataclasses
import sqlite3
import textwrap
import databases
import toml
import bcrypt
from quart import Quart, g, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from utils.queries import *
from utils.functions import check_pos_valid_letter


app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)


# Schema classes for data receive from client
@dataclasses.dataclass
class User: 
    username: str
    password: str 

@dataclasses.dataclass
class GuessWord:
    user_id: int
    game_id: int
    guess_word: str

@dataclasses.dataclass
class Game:
    id: int
    user_id: int
    correct_word: str
    win: bool
    num_of_guesses: int

@dataclasses.dataclass
class UserId:
    user_id: int


# DATABASE CONNECTION
async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database

def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db

@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()


# Handle bad routes/errors
@app.errorhandler(404)
def not_found(e):
    return {"error": "404 The resource could not be found"}, 404

@app.errorhandler(RequestSchemaValidationError) 
def bad_request(e):
    return {"error": str(e.validation_error)}, 400

@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409

@app.errorhandler(401)
def unauthorize(e):
    return str(e), 401

# API code here for Python people
# ***************************** TEST ROUTES ********************************** 


@app.route("/", methods=["GET"])
def wordle():
    """Game Route (dev only)"""
    return textwrap.dedent( """<h1>Welcome to wordle api project Game service</h1>
                <p>Vu Diep</p>
    """)



# Get a game by id show the correct word for testing
@app.route("/game/<int:id>", methods=["GET"])
async def get_game(id):
    """Get the correct word for a game by game_id (dev only)"""
    db = await _get_db()
    game = await db.fetch_one(
        "SELECT * FROM game WHERE id = :id", 
        values={"id": id}
    )
    app.logger.info('SELECT * FROM game WHERE id = :id')
    if game:
        return dict(game)
    else:
        abort(404)



# Get all games from users
# <int:id> -> user id
# return -> Array [{
#   id: int
#   num_of_guesses: int
#   user_id: int
#   win: bool   
# }]
@app.route("/game/user/<int:user_id>", methods=["GET"])
async def get_all_games_user(user_id):
    """Get all games from a user id, ( win, lose and in progress )
        {id} = user's id
    """
    db = await _get_db()
    user_game_active = await db.fetch_all(
        """SELECT id, num_of_guesses, user_id, win from game 
            WHERE user_id=:user_id""",
    values={"user_id": user_id}
    )
    app.logger.info("SELECT id, num_of_guesses, user_id, win from game WHERE user_id=:user_id")
    if user_game_active:
        return list(map(dict, user_game_active))
    else:
        abort(404)


# Get all games in progress from users,
# <int:id> -> user id
# return -> Array [{
#   id: int
#   num_of_guesses: int
#   user_id: int
#   win: bool   
# }]
@app.route("/game/user/allGamesInProgress/<int:user_id>", methods=["GET"])
async def get_all_games_in_progress_user(user_id):
    """Get all games that are in progress from a user id, won/lost games will not display
        {id} = user's id
    """
    db = await _get_db()
    user_game_active = await db.fetch_all(
        """SELECT id, num_of_guesses, user_id, win from game 
            WHERE user_id=:user_id AND win != true AND num_of_guesses < 6""",
    values={"user_id": user_id}
    )

    app.logger.info("""SELECT id, num_of_guesses, user_id, win from game 
            WHERE user_id=:user_id AND win != true AND num_of_guesses < 6""")

    if user_game_active:
        return list(map(dict, user_game_active))
    else:
        abort(404)


# Get a specific game in progress from user id
# user_id: -> int, user's id
# game_id: -> int, user's id
@app.route("/game/<int:user_id>/<int:game_id>")
async def get_user_game_in_progress(user_id, game_id):
    """Get a game in progress"""
    db = await _get_db()

    guess_word_list = await get_guesswords_in_game(
        game_id=game_id, 
        user_id=user_id, 
        db=db,
        app=app
    )
    game_data = await get_game_by_id(
        game_id=game_id, 
        user_id=user_id, 
        db=db,
        app=app
    )

    if not game_data:
        abort(404)

    game_data["currentGuessWords"] = guess_word_list
    return game_data


# Start a Game
# Param: data -> JSON {"user_id": int}
@app.route("/game/user/startNewGame", methods=["POST"])
@validate_request(UserId)
async def start_user_new_game(data):
    """Add a new game into database"""
    db = await _get_db()
    user_data = dataclasses.asdict(data)
    user_id = user_data["user_id"]
    user = get_one_user(id=user_id, db=db, app=app)
    if user:
        game_id = await add_new_game(user_id=user_id, db=db)
        return {"game_id": game_id, "user_id": user_id}
    return abort(404)




# Add a guess word from user to database
# Param: 
# data -> JSON {
#   "id": int
#   "user_id": int
#   "guess_word": str
# }
@app.route("/game/addGuessWord", methods=["POST"])
@validate_request(GuessWord)
async def post_user_guessword(data):
    """Add a guessword into database"""
    db = await _get_db()
    user_guessed = dataclasses.asdict(data)  # Data from POST req

    game_id = user_guessed["game_id"]
    user_id = user_guessed["user_id"]
    guess_word = user_guessed["guess_word"]

    current_game_guesswords_list = await get_guesswords_in_game(user_id=user_id, game_id=game_id, db=db, app=app)

    num_of_guesses = await get_game_num_guesses(id=game_id, user_id=user_id, db=db, app=app)
    won = await get_win_query(id=game_id, user_id=user_id, db=db, app=app) 

    # User and game doesn't exist
    if not num_of_guesses or not won: 
        return abort(404)

    # Game already won or lost
    if num_of_guesses[0] >= 6 or won[0]:   
        return {"numberOfGuesses": num_of_guesses[0], "win": won[0]}

    # Check if user already guess the word before
    if guess_word in current_game_guesswords_list:
        return {"error": "Cannot enter the same word twice"}

    # Proceed to check
    correct_word = await get_game_correct_word(id=game_id, user_id=user_id ,db=db, app=app)
    isValid = False
    isCorrectWord = False

    # Serialize valid data into an array
    d = await db.fetch_all("SELECT * FROM valid")
    VALID_DATA = [item for t in d for item in t]

    try:
        if guess_word in VALID_DATA:     
            await add_user_guessed_word(
                id=game_id, 
                user_id=user_id, 
                guess_word=guess_word, 
                db=db
            )

            if guess_word == correct_word:
                await set_win_user(id=game_id, user_id=user_id, db=db)
                letter_map = {
                    'correctPosition' : list(range(6)),
                    'correctLetterWrongPos': [],
                    'wrongLetter' : []
                }
                await increment_guesses(id=game_id, user_id=user_id, db=db)
                isCorrectWord=True

            else:
                letter_map = check_pos_valid_letter(
                    guess_word=guess_word, 
                    correct_word=correct_word
                )
                await increment_guesses(id=game_id, user_id=user_id, db=db)
            isValid = True
        else:
            return {"error": "Invalid word"}

    except sqlite3.IntegrityError as e:
        abort(409, e)

    responseData = {
        "guessesRemain": 6 - num_of_guesses[0] - 1,
        "isValid": isValid,
        "correctWord": isCorrectWord,
        "letterPosData": letter_map
    }
    return responseData, 201    # Return Response
