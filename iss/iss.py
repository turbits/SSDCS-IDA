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
IDA_ISS_SHARED_KEY = os.getenv("IDA_ISS_SHARED_KEY")
ISS_HOST = os.getenv("ISS_HOST")
ISS_PORT = int(os.getenv("ISS_PORT"))
ISS_DEBUG = os.getenv("ISS_DEBUG")
ISS_TARGET_URL = os.getenv("ISS_TARGET_URL")
ISS_SEND_TIMEOUT = int(os.getenv("ISS_SEND_TIMEOUT"))
ISS_SEND_DELAY = int(os.getenv("ISS_SEND_DELAY"))

if not IDA_ISS_SHARED_KEY:
    raise ValueError("Fernet key not found in .env")
fernet = Fernet(IDA_ISS_SHARED_KEY.encode())


# =================== APP ===================
iss = Flask(__name__)
lock = threading.Lock()


# =================== MAIN ===================
def send_data():
    try:
        # record = the whole object
        # name = the name of the record
        # file = the "file" property of the record

        # generating a random int for the length of the name prop
        record_name_length = random.randint(4, 10)
        # generating a random int for the length of the file prop
        record_file_length = random.randint(10, 50)
        # storing ascii letters (upper/lower) and digits (0-9) in variables
        letters = string.ascii_letters
        digits = string.digits

        # we craft a random string for the "name" property
        rand_name = f"RECORD-{''.join(random.choice(letters + digits) for i in range(record_name_length))}"

        # now we craft a random string for the "file" property.
        # this serves as the "data" portion of the record that the ISS is transmitting, presumably retrieved from some instrument or sensor that is collecting data on the ISS.
        rand_file = ''.join(random.choice(letters + digits) for i in range(record_file_length))

        # encoding the random file string to b64 for the "file" property
        # this is split into steps to show the process more clearly
        # 1. this will return a bytes object (b'<str>')
        rand_file_enc = rand_file.encode()
        # 2. this will return a bytes object, but it will be encoded to b64 (b'<str>')
        rand_file_b64 = base64.b64encode(rand_file_enc)
        # 3. finally, this will return a string (decoding from a bytes object to a string)
        rand_file_b64_string = rand_file_b64.decode()

        # the end result is a 'file' property that originally had a random string as its value, was then encoded to b64 (which returns a byte object), then decoded from a bytes object to a string so we can use it in the record dict that we will encrypt (using Fernet encryption) and then send to IDA

        # now compile data into a 'record' dict
        # we dont include the created_at, updated_at, or id properties as these are generated when needed by IDA
        record_data = {
            "name": rand_name,
            "file": {
                "data": rand_file_b64_string
            }
        }

        # convert the record dictionary to a json object
        record_json = json.dumps(record_data)
        # encrypt the record json object using Fernet and our shared key (returns a bytes object)
        encrypted_data = fernet.encrypt(record_json.encode())
        # and then we have to decode it from a bytes object to a string again
        # this is our final payload, our whole record, encrypted and ready to send to IDA
        payload = encrypted_data.decode()

        # send the request to IDA
        print("🧑‍🚀 ISS: Sending payload to IDA")

        res = requests.post(ISS_TARGET_URL, data=payload, headers={"Content-Type": "application/text"}, timeout=ISS_SEND_TIMEOUT)

        print(f"🌍 ISS: Response from IDA: {res.status_code}\n{res.text}")
    except Exception as e:
        print(f"⚠️ ISS-ERR: {str(e)}")


def start_iss_data_loop():
    threading.Timer(ISS_SEND_DELAY, start_recurring_process).start()


def start_recurring_process():
    while True:
        lock.acquire()
        send_data()
        lock.release()
        time.sleep(ISS_SEND_DELAY)


if __name__ == '__main__':
    t = threading.Thread(target=start_iss_data_loop)
    t.daemon = True
    t.start()
    # debug mode is off, otherwise for some reason the send_data gets called twice at the same time..
    iss.run(host=ISS_HOST, port=ISS_PORT, debug=False)
