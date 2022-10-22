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
    """Home Route (dev only)"""
    return textwrap.dedent( """<h1>Welcome to wordle api project 1</h1>
                <p>Vu Diep</p>
    """)

# Get a game by id show the correct word for testing
@app.route("/game/<int:id>", methods=["GET"])
async def get_game(id):
    """Get a game by game_id (dev only)"""
    db = await _get_db()
    game = await db.fetch_one(
        "SELECT * FROM game WHERE id = :id", 
        values={"id": id}
    )
    if game:
        return dict(game)
    else:
        abort(404)


# *************************************************************************   
# Register User Route
# Param
# data -> JSON {
#   "username": str
#   "password": str
# }
@app.route("/user/register", methods=["POST"])
@validate_request(User)
async def register(data):
    """Register Route"""
    db = await _get_db()
    user = dataclasses.asdict(data)

    password = user['password']    # hash password with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(
        password.encode('UTF-8'), salt).decode('UTF-8')

    try:
        user_id = await add_user(username=user["username"], password=str(hashed), db=db)

    except sqlite3.IntegrityError as e:
        abort(409, e)

    await add_new_game(user_id=user_id, db=db)  # automatically start a new game 

    return {"authenticated": True, "username": user["username"]}, 201, {"Location": f"/user/{user_id}"}


# Login Route
# Param:
# data -> JSON {
#   "username": str
#   "password": str
# }
@app.route("/user/login", methods=["POST"])
@validate_request(User)
async def login(data):
    """ Login Route
    Provide username and password to login
    """
    db = await _get_db()
    authenticated = False
    userInput = dataclasses.asdict(data)
    username = userInput['username']
    password = userInput['password']

    user = await get_user_by_username(username=username, db=db)
    
    if user:        
        actualPassword = user[2]
        if bcrypt.checkpw(password.encode('UTF-8'), actualPassword.encode('UTF-8')):
            authenticated=True
            
    if authenticated:
        return {"authenticated" : authenticated}
    else:
        abort(401)


# Add a guess word from user to database
# Param: 
# data -> JSON {
#   "id": int
#   "user_id": int
#   "guess_word": str
# }
@app.route("/user/addGuess", methods=["POST"])
@validate_request(GuessWord)
async def post_user_guessword(data):
    """Add a guessword into database"""
    db = await _get_db()
    user_guessed = dataclasses.asdict(data)  # Data from POST req

    game_id = user_guessed["game_id"]
    user_id = user_guessed["user_id"]
    guess_word = user_guessed["guess_word"]

    current_game_guesswords_list = await get_guesswords_in_game(user_id=user_id, game_id=game_id, db=db)

    num_of_guesses = await get_game_num_guesses(id=game_id, user_id=user_id, db=db)
    won = await get_win_query(id=game_id, user_id=user_id, db=db) 

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
    correct_word = await get_game_correct_word(id=game_id, user_id=user_id ,db=db)
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


# Start a Game
# Param: data -> JSON {"user_id": int}
@app.route("/user/startNewGame", methods=["POST"])
@validate_request(UserId)
async def start_user_new_game(data):
    """Add a new game into database"""
    db = await _get_db()
    user_data = dataclasses.asdict(data)
    user_id = user_data["user_id"]
    user = get_one_user(id=user_id, db=db)
    if user:
        game_id = await add_new_game(user_id=user_id, db=db)
        return {"game_id": game_id, "user_id": user_id}
    return abort(404)



# Get all games from users
# <int:id> -> user id
# return -> Array [{
#   id: int
#   num_of_guesses: int
#   user_id: int
#   win: bool   
# }]
@app.route("/user/allGames/<int:user_id>", methods=["GET"])
async def get_all_games_user(user_id):
    """Get all games from a user id
        {id} = user's id
    """
    db = await _get_db()
    user_game_active = await db.fetch_all(
        """SELECT id, num_of_guesses, user_id, win from game 
            WHERE user_id=:user_id""",
    values={"user_id": user_id}
    )
    if user_game_active:
        return list(map(dict, user_game_active))
    else:
        abort(404)


# Get a specific game in progress from user id
# user_id: -> int, user's id
# game_id: -> int, user's id
@app.route("/user/game/<int:user_id>/<int:game_id>")
async def get_user_game_in_progress(user_id, game_id):
    """Get a game in progress"""
    db = await _get_db()

    guess_word_list = await get_guesswords_in_game(
        game_id=game_id, 
        user_id=user_id, 
        db=db
    )
    game_data = await get_game_by_id(
        game_id=game_id, 
        user_id=user_id, 
        db=db
    )

    if not game_data:
        abort(404)

    game_data["currentGuessWords"] = guess_word_list
    return game_data


# Get all games in progress from users
# <int:id> -> user id
# return -> Array [{
#   id: int
#   num_of_guesses: int
#   user_id: int
#   win: bool   
# }]
@app.route("/user/allGamesInProgress/<int:user_id>", methods=["GET"])
async def get_all_games_in_progress_user(user_id):
    """Get all games that are in progress from a user id
        {id} = user's id
    """
    db = await _get_db()
    user_game_active = await db.fetch_all(
        """SELECT id, num_of_guesses, user_id, win from game 
            WHERE user_id=:user_id AND win != true AND num_of_guesses < 6""",
    values={"user_id": user_id}
    )
    if user_game_active:
        return list(map(dict, user_game_active))
    else:
        abort(404)