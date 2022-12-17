# 449 Back-end Project-01  10/22/2022
# Team members:
# Vu Diep

from itertools import cycle
import dataclasses
import sqlite3
import textwrap
import databases
import toml
from quart import Quart, g, abort, request
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from utils.queries import *
from utils.functions import check_pos_valid_letter, add_to_leaderboard
import uuid
from redis import Redis
from rq import Queue
from rq import Retry, Queue
from rq.registry import FailedJobRegistry

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
    username: str
    game_id: str
    guess_word: str

@dataclasses.dataclass
class Game:
    id: str
    username: str
    correct_word: str
    win: bool
    num_of_guesses: int

@dataclasses.dataclass
class Username:
    username: str

@dataclasses.dataclass
class Webhooks:
    url: str

# Global Variables
iterator = cycle([0, 1, 2])
q = Queue(connection=Redis())
registry = FailedJobRegistry(queue=q)

# DATABASE CONNECTION
async def _connect_db(num):
    if num == 1:
        database = databases.Database(app.config["DATABASES"]["URL1"])
        await database.connect()
        return database
    elif num == 2:
        database = databases.Database(app.config["DATABASES"]["URL2"])
        await database.connect()
        return database
    else:
        database = databases.Database(app.config["DATABASES"]["URL"])
        await database.connect()
        return database


def _get_db(num):
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db(num)
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


@app.route("/game/", methods=["GET"])
def wordle():
    """Game Route (dev only)"""
    return textwrap.dedent( """<h1>Welcome to wordle api project Game service</h1>
                <p>Vu Diep</p>
    """)



# Get a game by id show the correct word for testing
@app.route("/game/<string:id>", methods=["GET"])
async def get_game(id):
    """Get the correct word for a game by game_id (dev only)"""

    db = await _get_db(0)
    game = await db.fetch_one(
        "SELECT * FROM game WHERE id = :id", 
        values={"id": id}
    )
    app.logger.info('SELECT * FROM game WHERE id = :id')
    if game:
        return dict(game)
    else:
        abort(404)

# ********************************************************************************* 

@app.route("/game/webhook", methods=["POST"])
@validate_request(Webhooks)
async def register_webhook(data):
    db = await _get_db(0)
    input_data = dataclasses.asdict(data)
    print("here")
    callback_url = input_data["url"]
    try:
        await db.execute("INSERT INTO webhook (url) VALUES (:url)", values={"url": callback_url})

    except sqlite3.IntegrityError as e:
        abort(409, e)

    return {"url" : callback_url}, 200 


# Get all games from users
# <int:id> -> user id
# return -> Array [{
#   id: int
#   num_of_guesses: int
#   username: str
#   win: bool   
# }]
@app.route("/game/user/<string:username>", methods=["GET"])
async def get_all_games_user(username):
    """Get all games by a username, ( win, lose and in progress )
        {username} = username
    """
    
    num = next(iterator)
    print(num)
    db = await _get_db(num)


    user_game_active = await db.fetch_all(
        """SELECT id, num_of_guesses, username, win from game 
            WHERE username=:username""",
    values={"username": username}
    )
    app.logger.info("SELECT id, num_of_guesses, username, win from game WHERE username=:username")
    if user_game_active:
        return list(map(dict, user_game_active))
    else:
        abort(404)


# Get all games in progress from users,
# <int:id> -> user id
# return -> Array [{
#   id: int
#   num_of_guesses: int
#   username: str
#   win: bool   
# }]
@app.route("/game/user/gamesinprogress/<string:username>", methods=["GET"])
async def get_all_games_in_progress_user(username):
    """Get all games that are in progress from a username, won/lost games will not display
    """

    num = next(iterator)
    db = await _get_db(num)

    user_game_active = await db.fetch_all(
        """SELECT id, num_of_guesses, username, win from game 
            WHERE username=:username AND win != true AND num_of_guesses < 6""",
    values={"username": username}
    )

    app.logger.info("""SELECT id, num_of_guesses, username, win from game 
            WHERE username=:username AND win != true AND num_of_guesses < 6""")

    if user_game_active:
        return list(map(dict, user_game_active))
    else:
        abort(404)


# Get a specific game in progress from user id
# username: -> str
# game_id: -> int, user's id
@app.route("/game/<string:username>/<string:game_id>")
async def get_user_game_in_progress(username, game_id):
    """Get a game in progress"""
    
    num = next(iterator)
    db = await _get_db(num)

    guess_word_list = await get_guesswords_in_game(
        game_id=game_id, 
        username=username, 
        db=db,
        app=app
    )
    game_data = await get_game_by_id(
        game_id=game_id, 
        username=username, 
        db=db,
        app=app
    )

    if not game_data:
        abort(404)

    game_data["currentGuessWords"] = guess_word_list
    return game_data


# Start a Game
# Param: data -> JSON {"username": str}
@app.route("/game/user/start", methods=["POST"])
@validate_request(Username)
async def start_user_new_game(data):
    """Add a new game into database and return the game_id"""
    db = await _get_db(0)
    user_data = dataclasses.asdict(data)
    username = user_data["username"]
    game_id = uuid.uuid4()
    await add_new_game(game_id=game_id, username=username, db=db)

    return {"game_id": game_id, "username": username}
    

# Add a guess word from user to database
# Param: 
# data -> JSON {
#   "id": int
#   "username": str
#   "guess_word": str
# }
@app.route("/game/guess", methods=["POST"])
@validate_request(GuessWord)
async def post_user_guessword(data):
    """Add a guessword into database"""
    db = await _get_db(0)
    user_guessed = dataclasses.asdict(data)  # Data from POST req

    game_id = user_guessed["game_id"]
    username = user_guessed["username"]
    guess_word = user_guessed["guess_word"]

    current_game_guesswords_list = await get_guesswords_in_game(username=username, game_id=game_id, db=db, app=app)

    num_of_guesses = await get_game_num_guesses(id=game_id, username=username, db=db, app=app)
    won = await get_win_query(id=game_id, username=username, db=db, app=app) 

    # User and game doesn't exist
    if not num_of_guesses or not won: 
        return abort(404)

    leaderboard_data={
        "game_id" : game_id,
        "num_of_guesses": num_of_guesses[0],
        "username": username,
        "win": won[0]
    }

    # Game already won or lost
    if num_of_guesses[0] >= 6 or won[0]:
        return {"numberOfGuesses": num_of_guesses[0], "win": won[0]}

    # Check if user already guess the word before
    if guess_word in current_game_guesswords_list:
        return {"error": "Cannot enter the same word twice"}

    # Proceed to check
    correct_word = await get_game_correct_word(id=game_id, username=username ,db=db, app=app)
    isValid = False
    isCorrectWord = False

    # Serialize valid data into an array
    d = await db.fetch_all("SELECT * FROM valid")
    VALID_DATA = [item for t in d for item in t]

    try:
        if guess_word in VALID_DATA:     
            await add_user_guessed_word(
                id=game_id, 
                username=username, 
                guess_word=guess_word, 
                db=db
            )

            if guess_word == correct_word:
                await set_win_user(id=game_id, username=username, db=db)
                # Add to redis queue
                leaderboard_data["num_of_guesses"] += 1
                leaderboard_data["win"] = True
                q.enqueue(add_to_leaderboard, leaderboard_data, retry=Retry(max=3, interval=5))
                letter_map = {
                    'correctPosition' : list(range(6)),
                    'correctLetterWrongPos': [],
                    'wrongLetter' : []
                }
                await increment_guesses(id=game_id, username=username, db=db)
                isCorrectWord=True

            else:
                if num_of_guesses[0] == 5:
                    leaderboard_data["num_of_guesses"] += 1
                    leaderboard_data["win"] = False
                    # Add to redis queue
                    q.enqueue(add_to_leaderboard, leaderboard_data, retry=Retry(max=3, interval=5))

                letter_map = check_pos_valid_letter(
                    guess_word=guess_word, 
                    correct_word=correct_word
                )
                await increment_guesses(id=game_id, username=username, db=db)
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




