import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

# DATABASE CONNECTION
@dataclasses.dataclass
class User:
    username: str
    password: str

@dataclasses.dataclass
class GuessWord:
    user_id: int
    guess_word: str

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
    all_users = await db.fetch_all('SELECT * from users;')
    return list(map(dict, all_users))

# Get single user
@app.route("/user/<int:id>", methods=["GET"])
async def get_one_user(id):
    db = await _get_db()
    user = await db.fetch_one("SELECT * FROM users WHERE id = :id", values={"id": id})
    if user:
        return dict(user)
    else:
        abort(404)

# Add user example
@app.route("/user/register", methods=["POST"])
@validate_request(User)
async def register(data):
    db = await _get_db()
    user = dataclasses.asdict(data)
    # hash this before adding to db user['password']
    try:
        id = await db.execute(
            """
            INSERT INTO users(username, password)
            VALUES(:username, :password)
            """,
            user,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    user["id"] = id
    return user, 201, {"Location": f"/user/{id}"}


@app.route("/user/guessword/<int:id>", methods=["GET"])
async def get_guessword(id):
    db = await _get_db()
    guess_word = await db.fetch_all('SELECT guess_word from userInput WHERE user_id=:id;', values={"id": id})
    return list(map(dict, guess_word))


# @app.route("/user/guessword/<int:id>", methods=["POST"])
# @validate_request(GuessWord)
# async def post_guessword(data):
#     db = await _get_db()
#     user = dataclasses.asdict(data)
#     # hash this before adding to db user['password']
#     try:
#         id = await db.execute(
#             """
#             INSERT INTO users(username, password)
#             VALUES(:username, :password)
#             """,
#             user,
#         )
#     except sqlite3.IntegrityError as e:
#         abort(409, e)

#     user["id"] = id
#     return user, 201, {"Location": f"/user/{id}"}