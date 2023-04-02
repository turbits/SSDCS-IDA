import os
import sys
import signal
from bottle import Bottle, run, debug, static_file, abort, error, route

ida_app = Bottle()

# the key should be well secured on a real app; in .env, etc. this is just for protoype purposes
IDA_ISS_SHARED_KEY = "JahXa-F9qAgyuLoCYMkGzrfMfg-itIZLpz6-73Furp0="


# sys.path.insert(0, os.path.dirname("routes/"))


# set up static file serving (for things like css static path, js, etc.)
# if you need to access a static file it should be as simple as putting the file in the /static folder
# and accessing it as <filename> (e.g. css/style.css in IDAs case
@ida_app.route("/<filename:path>")
def send_static(filename):
    return static_file(filename, root="static/")


# =================== ROUTES ===================
# can ignore these flake8 errors, this structure is easier to read and understand.
# importing each route file here allows us to keep the routes in separate files
# making this file and the routes files easier to read and understand
# noqa is used here to ignore the flake8 errors from a linting perspective
# if this were a real product, you should not do this
from routes import users, default, logs, records  # noqa: E402, F401


@ida_app.error(404)
def error404(e):
    abort("404")


def stop_app(signal, frame):
    print("🟢 OK: IDA stopped")
    sys.exit(0)


# handle SIGINT (ctrl+c)
signal.signal(signal.SIGINT, stop_app)

# run the IDA app on localhost:8080; reloader will restart the server when a file is changed
ida_app.run(host='localhost', port=8080, debug=False, reloader=True)
