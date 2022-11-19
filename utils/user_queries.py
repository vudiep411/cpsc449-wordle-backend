# Register a user in database
# username -> str, username from request data
# password -> str, password from request data
# return user_id -> int, newly created user's id
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


# Get user by username
# username -> str, username from request data
# return tuple(id:int, username:str, password:str)
async def get_user_by_username(username, db, app):
    user = await db.fetch_one("SELECT * from users WHERE username=:username",
    values={"username": username}
    )
    app.logger.info("SELECT * from users WHERE username=:username")
    return user