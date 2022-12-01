import dataclasses
import textwrap
import redis
from quart import Quart, g, abort, request
from quart_schema import QuartSchema, RequestSchemaValidationError


app = Quart(__name__)
QuartSchema(app)


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


# Leaderboard
@app.route("/leaderboard/", methods=["GET"])
def leaderboard():
    """Leader Board Routes"""
    # r = redis.Redis(host='localhost', port=6379, db=0)
    return textwrap.dedent( """<h1>Welcome to Leaderboard service</h1>
                <p>Vu Diep</p>
    """)