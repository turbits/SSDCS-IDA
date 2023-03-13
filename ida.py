import sqlite3
import os
from bottle import Bottle, run, route, debug, template, static_file, abort

app = Bottle()

# any "os.getenv" is getting values from the .env file
# .env should be in the project root (same level as this file)


@app.route("/<filename:path>")
def send_static(filename):
    return static_file(filename, root="static/")


@app.route("/")
def index():
    return template("templates/index.tpl")


@app.error(404)
def error404(error):
    abort("404")


debug(os.getenv("DEBUG", False))
run(app, host='localhost', port=8080, reloader=os.getenv("RELOADER", False))
