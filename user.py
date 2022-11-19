import dataclasses
import sqlite3
import textwrap
import databases
import toml
import bcrypt
from quart import Quart, g, abort, request
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from utils.queries import *


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
    return str(e), 401, {"WWW-Authenticate": 'Basic realm=User Login'}


@app.route("/user/", methods=["GET"])
def user():
    """User Route (dev only)"""
    return textwrap.dedent( """<h1>Welcome to User service</h1>
                <p>Vu Diep</p>
    """)

@app.route("/", methods=["GET"])
def home():
    """Home Route (dev only)"""
    return textwrap.dedent( """<h1>Welcome to wordle API services</h1>
                <p>Vu Diep</p>
    """)


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

    return {"authenticated": True, "username": user["username"]}, 201, {"Location": f"/user/{user_id}"}


# Login Route
# Param:
# data -> JSON {
#   "username": str
#   "password": str
# }
@app.route("/user/login", methods=["POST"])
async def login():
    """ Login Route
    Provide username and password to login
    """
    auth = request.authorization
    print(auth)
    # return bad request if invalid auth header
    if not auth:
        abort(401)

    # check both username and password are present
    if not auth.username or not auth.password:
        abort(401)

    db = await _get_db()
    authenticated = False

    username = auth.username
    password = auth.password

    user = await get_user_by_username(username=username, db=db, app=app)
    
    if user:        
        actualPassword = user[1]
        if bcrypt.checkpw(password.encode('UTF-8'), actualPassword.encode('UTF-8')):
            authenticated=True
            
    if authenticated:
        return {"authenticated" : authenticated}
    else:
        abort(401)
