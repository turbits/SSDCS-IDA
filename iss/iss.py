import time
import os
import random
import string
import base64
import sys
import json
import signal
import threading
import requests
from flask import Flask
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

# =================== ENV ===================
# the key and config should be well secured on a real app; the .env is pushed with this repo but in a real project you would never expose secrets
IDA_ISS_SHARED_KEY = os.getenv("IDA_ISS_SHARED_KEY")
ISS_HOST = os.getenv("ISS_URL")
ISS_PORT = os.getenv("ISS_PORT")
ISS_DEBUG = os.getenv("ISS_DEBUG")
ISS_TARGET_URL = os.getenv("ISS_TARGET_URL")
ISS_SEND_TIMEOUT = os.getenv("ISS_SEND_TIMEOUT")

if not IDA_ISS_SHARED_KEY:
    raise ValueError("Fernet key not found in .env")
fernet = Fernet(IDA_ISS_SHARED_KEY.encode())


# =================== APP ===================
iss = Flask(__name__)
iss.host = ISS_HOST
iss.port = ISS_PORT
iss.debug = ISS_DEBUG


# =================== MAIN ===================
def send_data():
    while True:
        # generate random data
        data_name_length = random.randint(4, 10)  # gen random int from 4 to 10 (the length of `name` value)
        data_file_length = random.randint(10, 50)  # gen random int from 10 to 50 (the length of the `file['data']` value)
        letters = string.ascii_letters
        digits = string.digits
        rand_name_str = ''.join(random.choice(letters + digits) for i in range(data_name_length))
        rand_file_str = ''.join(random.choice(letters + digits) for i in range(data_file_length))
        rand_file_str_b64 = base64.b64encode(rand_file_str.encode('ascii'))

        # compile random data into a dict
        file_data = {
            "name": rand_name_str,
            "file": {
                "data": rand_file_str_b64.decode('ascii')
            }
        }

        # encrypt the file
        file_string = json.dumps(file_data)
        encrypted_data = fernet.encrypt(file_string.encode())

        try:
            # send request
            res = requests.post(ISS_TARGET_URL, data=encrypted_data, headers={"Content-Type": "application/octet-stream"})
            # print response to server console
            # print(f"🟢 ISS-RESPONSE: {res.read().decode()}")
            # sleep for <ISS_SEND_TIMEOUT> (default 10) seconds
            time.sleep(ISS_SEND_TIMEOUT)
        except Exception as e:
            print(f"🔴 ISS-ERR: {str(e)}")


if __name__ == '__main__':
    t = threading.Thread(target=send_data)
    t.daemon = True
    t.start()

    # run the ISS app; DEBUG mode will output debug info and reload the app on file change
    iss.run(host=ISS_HOST, port=ISS_PORT, debug=ISS_DEBUG)
