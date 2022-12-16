import dataclasses
import textwrap
import redis
from quart import Quart, g, abort, request
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
import json
import httpx
import time

app = Quart(__name__)
QuartSchema(app)

@dataclasses.dataclass
class GameData: 
    game_id: str
    username: str
    num_of_guesses: int
    win: bool

# Register with Game service

# error = True
# while error:
#     try:
#         time.sleep(1)
#         url = "https://webhook.site/68f8898e-78c7-46a6-9bfb-0ab6bcad684c"
#         r = httpx.post('http://localhost:5100/webhook', data={"url": url})
#         if r.status_code != 200:
#             error = True
#         else: 
#             error = False
#     except httpx.HTTPError as exc:
#         print(f"HTTP Exception for {exc.request.url} - {exc}")
#         print("Retrying...")
#         error = True


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


def get_redis_db():
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r

def get_score(guesses, win):
    if not win:
        return 0
    elif guesses == 1:
        return 6
    elif guesses == 2:
        return 5
    elif guesses == 3:
        return 4
    elif guesses == 4:
        return 3
    elif guesses == 5:
        return 2
    elif guesses == 6:
        return 1
    else:
        return 0

#Webhook
@app.route('/webhook', methods=['POST'])
async def webhook():
    push = await request.get_json()
    app.logger.debug(json.dumps(push, indent=2))
    return "", 204

# Leaderboard
@app.route("/leaderboard/", methods=["GET"])
def leaderboard():
    """Leader Board Routes"""
    # r = redis.Redis(host='localhost', port=6379, db=0)
    return textwrap.dedent( """<h1>Welcome to Leaderboard service</h1>
                <p>Vu Diep</p>
    """)


@app.route("/leaderboard/add", methods=["POST"])
@validate_request(GameData)
async def add_game(data):
    """ADD a game result"""
    game_data = dataclasses.asdict(data)
    game_id = game_data["game_id"]
    username = game_data["username"]
    win = game_data["win"]
    num_of_guesses = game_data["num_of_guesses"]

    r = get_redis_db()

    # Set data for a game
    r.hset(game_id, "win", int(win))
    r.hset(game_id, "username", username)
    r.hset(game_id, "num_of_guesses", num_of_guesses)

    # Average Score
    r.hincrby(username, "games")
    current_score = r.hget(username, "score")
    game_score = get_score(num_of_guesses, win)

    no_of_games = r.hget(username, "games")

    if current_score is not None:
        current_score = current_score.decode("utf-8")
    else:
        current_score = 0

    if no_of_games is not None:
        no_of_games = no_of_games.decode("utf-8")
    else:
        no_of_games = 1
    
    avg = (int(current_score) + int(game_score)) // int(no_of_games)
    r.hset(username, "score", avg)

    print(avg)
    # Set data for user
    r.zadd("players", {username: avg})

    return {
        "game_id": game_id, 
        "username": username, 
        "win": win, 
        "num_of_guesses": num_of_guesses
    }


@app.route("/leaderboard/players", methods=["GET"])
async def get_user():
    """GET TOP 10 result"""
    r = get_redis_db()
    arr = r.zrevrange("players", 0, -1, withscores=True)
    top_players = {}
    i = 0
    while i < len(arr) and i < 10:
        player = arr[i]
        top_players[i+1] = player[0].decode("utf-8")
        i += 1
        
    print(top_players)
    return top_players