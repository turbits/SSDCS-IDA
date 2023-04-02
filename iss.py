import time
import os
import random
import string
import base64
import sys
import json
import signal
import threading
import urllib.request
from cryptography.fernet import Fernet
from bottle import Bottle, route, response, request
# the key should be well secured on a real app; in .env, etc. this is just for protoype purposes

iss_app = Bottle()


# the key should be well secured on a real app; in .env, etc. this is just for protoype purposes
IDA_ISS_SHARED_KEY = "1z-L5ojvPur9pHsUD4EfYh1WhxlbFCvm8DdcEdcEPAc="


# ideally we'd pull this from .env or something
IDA_URL = "http://localhost:8080/records"
ISS_MICROSERVICE_PORT = 8081

if not IDA_ISS_SHARED_KEY:
    raise ValueError("Fernet key not found")
fernet = Fernet(IDA_ISS_SHARED_KEY.encode())


def start_microservice():
    print("🟢 OK(200): Microservice started")
    # run the ISS data microservice on port 8081
    iss_app.run(host="localhost", port=8081, debug=False, reloader=False)


def stop_microservice(signal, frame):
    print("🟢 OK(200): Microservice stopped")
    sys.exit(0)


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

        # craft request
        headers = {"Content-Type": "application/octet-stream"}
        req = urllib.request.Request(IDA_URL, headers=headers, data=encrypted_data)

        try:
            # send request
            res = urllib.request.urlopen(req)
            # print response to server console
            print(f"🟢 OK(200): {res.read().decode()}")
            # sleep for 3 seconds
            time.sleep(3)
        except Exception as e:
            print(f"🔴 ERROR: {str(e)}")


t = threading.Thread(target=send_data)
t.daemon = True
t.start()

# handle SIGINT (ctrl+c)
signal.signal(signal.SIGINT, stop_microservice)


def main():

    try:
        start_microservice()
    except Exception as e:
        print(f"🔴 ERROR: {str(e)}")


# run the ISS data microservice on port 8081
main()
