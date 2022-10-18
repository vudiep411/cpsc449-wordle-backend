import dataclasses
import sqlite3
import textwrap
import databases
import toml
import json
import bcrypt
from quart import Quart, g, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from utils.queries import add_new_game, get_one_user, get_correct_word_user, add_guessed_word, set_win_user, increment_guesses, get_game_guesses, get_win, add_user
from utils.functions import check_pos_valid_letter


app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

# Get the list of valid words
valid_f = open('valid.json')
VALID_DATA = json.load(valid_f)
valid_f.close()   
 

# DATABASE CONNECTION
@dataclasses.dataclass
class User:
    username: str
    password: str 

@dataclasses.dataclass
class GuessWord:
    user_id: int
    id: int
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

# ***********************************************************
# ------------------- YOUR CODE HERE ------------------------
# ***********************************************************
# API code here for Python people

# *****************************TEST ROUTES********************************** 

@app.route("/", methods=["GET"])
def wordle():
    return textwrap.dedent( """<h1>Welcome to wordle api project 1</h1>
                <p>Vu Diep</p>
    """)

# Get all users example for testing
@app.route("/user", methods=["GET"])
async def get_users():
    db = await _get_db()
    all_users = await db.fetch_all('SELECT username from users;')
    return list(map(dict, all_users))


# Get single user for testting
@app.route("/user/<int:id>", methods=["GET"])
async def get_user(id):
    db = await _get_db()
    return await get_one_user(id=id, db=db)


# *************************************************************************   

# Register User Route
# data -> JSON {
#   "username": str
#   "password": str
# }
@app.route("/user/register", methods=["POST"])
@validate_request(User)
async def register(data):
    db = await _get_db()
    user = dataclasses.asdict(data)

    password = user['password']    # hash password with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('UTF-8'), salt).decode('UTF-8')

    try:
        user_id = await add_user(username=user["username"], password=str(hashed), db=db)

    except sqlite3.IntegrityError as e:
        abort(409, e)

    await add_new_game(user_id=user_id, db=db)  # automatically start a new game 

    return {"authenticated": True, "username": user["username"]}, 201, {"Location": f"/user/{user_id}"}



# Login Route
# data -> JSON {
#   "username": str
#   "password": str
# }
@app.route("/user/login", methods=["POST"])
@validate_request(User)
async def login(data):
    db = await _get_db()
    authenticated = False
    userInput = dataclasses.asdict(data)
    username = userInput['username']
    password = userInput['password']

    user = await db.fetch_one("SELECT * from users WHERE username=:username",
    values={"username": username}
    )
    
# Check bcrypt hash
    if user:        
        actualPassword = user[2]
        if bcrypt.checkpw(password.encode('UTF-8'), actualPassword.encode('UTF-8')):
            authenticated=True

    return {"authenticated" : authenticated}



# Get guess word
@app.route("/user/guessword/<int:id>", methods=["GET"])
async def get_guessword(id):
    db = await _get_db()
    guess_word = await db.fetch_all('SELECT guess_word from userInput WHERE user_id=:id;', values={"id": id})
    return list(map(dict, guess_word))



# Add a guess word from user to database
# data -> JSON {
#   "id": <int:id>
#   "user_id": <int:id>
#   "guess_word": str
# }
@app.route("/user/guessword", methods=["POST"])
@validate_request(GuessWord)
async def post_guessword(data):
    db = await _get_db()
    user_guessed = dataclasses.asdict(data)  # Data from POST req

    id = user_guessed["id"]
    user_id = user_guessed["user_id"]
    guess_word = user_guessed["guess_word"]

    num_of_guesses = await get_game_guesses(id=id, user_id=user_id, db=db)
    won = await get_win(id=id, user_id=user_id, db=db) 

    # User and game doesn't exist
    if not num_of_guesses or not won: 
        return {"error" : "game does not exist"}

    # Game already won or lost
    if num_of_guesses[0] >= 6 or won[0]:   
        return {"numberOfGuesses": num_of_guesses[0], "win": won[0]}

    correct_word = await get_correct_word_user(id=id, user_id=user_id ,db=db)
    isValid = False
    isCorrectWord = False

    try:
        if guess_word in VALID_DATA:     
            await add_guessed_word(user_id=user_id, guess_word=guess_word, db=db)
            if guess_word == correct_word:
                await set_win_user(id=id, user_id=user_id, db=db)
                letter_map = {
                    'correctPosition' : [correct_word],
                    'correctLetterWrongPos': [],
                    'wrongLetter' : []
                }
                isCorrectWord=True
            else:
                letter_map = check_pos_valid_letter(guess_word=guess_word, correct_word=correct_word)
                await increment_guesses(id=id, user_id=user_id, db=db)
            isValid = True
        else:
            return {"error": "Invalid word"}

    except sqlite3.IntegrityError as e:
        abort(409, e)

    responseData = {
        "guessesRemain": 6 - num_of_guesses[0] + 1,
        "isValid": isValid,
        "correctWord": isCorrectWord,
        "letterPosData": letter_map
    }
    return responseData, 201    # Return Response



# Start a Game
# data -> JSON {"user_id": <int:id>}
@app.route("/user/startNewGame", methods=["POST"])
@validate_request(UserId)
async def start_new_game(data):
    db = await _get_db()
    user_id = dataclasses.asdict(data)
    game_id = await add_new_game(user_id=user_id["user_id"], db=db)

    return {"game_id": game_id, "user_id": user_id["user_id"]}



# Get a user's game 
# <int:id> -> game id
@app.route("/game/<int:id>", methods=["GET"])
async def get_game(id):
    db = await _get_db()
    game = await db.fetch_one("SELECT * FROM game WHERE id = :id", values={"id": id})
    if game:
        return dict(game)
    else:
        abort(404)



# Get all active game from users
# <int:id> -> user id
@app.route("/user/game/<int:id>", methods=["GET"])
async def get_all_games_user(id):
    db = await _get_db()
    user_game_active = await db.fetch_all(
        "SELECT id, num_of_guesses, user_id, win from game WHERE user_id=:user_id",
    values={"user_id": id}
    )
    return list(map(dict, user_game_active))

