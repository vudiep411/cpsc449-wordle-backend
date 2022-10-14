#!/bin/sh
chmod +xwr requirements.sh

python3 -m pip install databases[aiosqlite]
python3 -m pip install quart-schema
sudo apt install --yes python3-pip ruby-foreman sqlite3
python3 -m pip install --upgrade quart[dotenv] click markupsafe Jinja2