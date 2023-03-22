import os
import sys
from bottle import run, debug, static_file, abort, error, route

sys.path.insert(0, os.path.dirname("routes/"))

# any "os.getenv" is getting values from the .env file
# .env should be in the project root (same level as this file)


# set up static file serving (for things like css static path, js, etc.)
# if you need to access a static file it should be as simple as putting the file in the /static folder
# and accessing it as <filename> (e.g. css/style.css in IDAs case
@route("/<filename:path>")
def send_static(filename):
    return static_file(filename, root="static/")


# =================== ROUTES ===================
# can ignore these flake8 errors, this structure is easier to read and understand.
# importing each route file here allows us to keep the routes in separate files
# making this file and the routes files easier to read and understand
# noqa is used here to ignore the flake8 errors from a linting perspective
# if this were a real product, you should not do this
from routes import pages, logs, records, users  # noqa: E402, F401


@error(404)
def error404(error):
    abort("404")


# get debug env value, default to False
debug(os.getenv("DEBUG", False))
# run the app on localhost:8080, and reload if RELOADER env value is True; default to False
run(host='localhost', port=8080, reloader=os.getenv("RELOADER", False))
