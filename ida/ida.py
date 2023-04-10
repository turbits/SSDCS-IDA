import os
import sys
import signal
from flask import Flask, render_template
from routes.pages import pages_bp
from routes.errors import errors_bp
from routes.logs import logs_bp
from routes.records import records_bp
from routes.users import users_bp
from dotenv import load_dotenv

load_dotenv()

# =================== ENV ===================
# the key and config should be well secured on a real app; the .env is pushed with this repo but in a real project you would never expose secrets
IDA_ISS_SHARED_KEY = os.getenv("IDA_ISS_SHARED_KEY")
IDA_HOST = os.getenv("IDA_HOST")
IDA_PORT = os.getenv("IDA_PORT")
IDA_DEBUG = os.getenv("IDA_DEBUG")
IDA_SECRET_KEY = os.getenv("IDA_SECRET_KEY")

if not IDA_ISS_SHARED_KEY:
    raise ValueError("Fernet key not found in .env")


# =================== APP ===================
ida = Flask(__name__)
ida.secret_key = IDA_SECRET_KEY

# =================== ROUTES ===================
ida.register_blueprint(pages_bp)
ida.register_blueprint(errors_bp)
ida.register_blueprint(logs_bp)
ida.register_blueprint(records_bp)
ida.register_blueprint(users_bp)


# =================== MAIN ===================
if __name__ == '__main__':
    ida.run(host=IDA_HOST, port=IDA_PORT, debug=True)
