
import dataclasses
import sqlite3
import textwrap


import databases
import toml
import json
import bcrypt
from quart import Quart, g, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from utils.queries import add_new_game, get_one_user, get_correct_word_user, add_guessed_word, set_win_user, increment_guesses, get_game_guesses
from utils.functions import check_pos_valid_letter


app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

# Generate a correct word


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

# **********************************************************
# ------------------- YOUR CODE HERE -----------------------
# ***********************************************************
# API code here for Python people


@app.route("/", methods=["GET"])
def wordle():
    return textwrap.dedent( """<h1>Welcome to wordle api project 1</h1>
                <p>Vu Diep</p>
    """)

# Get all users example
@app.route("/user", methods=["GET"])
async def get_users():
    db = await _get_db()
    all_users = await db.fetch_all('SELECT username from users;')
    return list(map(dict, all_users))


# Get single user
@app.route("/user/<int:id>", methods=["GET"])
async def get_user(id):
    db = await _get_db()
    return await get_one_user(id=id, db=db)

    
# Register User Route
@app.route("/user/register", methods=["POST"])
@validate_request(User)
async def register(data):
    db = await _get_db()
    user = dataclasses.asdict(data)

    password = user['password']    # hash password wiht bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('UTF-8'), salt).decode('UTF-8')

    try:
        user_id = await db.execute(
            """
            INSERT INTO users(username, password)
            VALUES(:username, :password)
            """,
            values={"username": user["username"], "password": str(hashed)},
        )

    except sqlite3.IntegrityError as e:
        abort(409, e)

    await add_new_game(user_id=user_id, db=db)

    return {"authenticated": True, "username": user["username"]}, 201, {"Location": f"/user/{user_id}"}


# Login Route
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
   
    if user:    # Check bcrypt hash
        actualPassword = user[2]
        print(actualPassword)
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
@app.route("/user/guessword", methods=["POST"])
@validate_request(GuessWord)
async def post_guessword(data):
    db = await _get_db()
    guessed = dataclasses.asdict(data)
    id = guessed["id"]
    user_id = guessed["user_id"]
    guess_word = guessed["guess_word"]

    guesses = await get_game_guesses(id=id, user_id=user_id, db=db)
    won = await db.fetch_one('SELECT win FROM game WHERE user_id=:user_id AND id=:id',
        values={"user_id": user_id, "id": id}
    )

    if guesses[0] >= 6 or won[0]:
        return {"numberOfGuesses": guesses[0], "win": won[0]}

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
        "guessesRemain": 6 - guesses[0],
        "isValid": isValid,
        "correctWord": isCorrectWord,
        "letterPosData": letter_map
    }
    return responseData, 201

# Start a Game
@app.route("/user/startNewGame", methods=["POST"])
@validate_request(UserId)
async def start_new_game(data):
    db = await _get_db()
    user_id = dataclasses.asdict(data)
    game_id = await add_new_game(user_id=user_id["user_id"], db=db)
    print(game_id)
    return {"game_id": game_id, "user_id": user_id["user_id"]}


# Get a user's game 
@app.route("/game/<int:id>", methods=["GET"])
async def get_game(id):
    db = await _get_db()
    game = await db.fetch_one("SELECT * FROM game WHERE id = :id", values={"id": id})
    if game:
        return dict(game)
    else:
        abort(404)

# Get all active game from users
@app.route("/user/game/<int:id>", methods=["GET"])
async def get_all_games_user(id):
    print(id)
    db = await _get_db()
    user_game_active = await db.fetch_all(
        "SELECT id, num_of_guesses, user_id, win from game WHERE user_id=:user_id AND win=False",
    values={"user_id": id}
    )
    return list(map(dict, user_game_active))

