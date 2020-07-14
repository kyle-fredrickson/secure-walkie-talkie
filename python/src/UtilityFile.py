import json

import UtilityProtocol as up

def receive_message(input):
    if type(input) is bytes:
        data = input
    else:
        with open(input, "rb") as f:
            data = f.read()

    return (data[:up.HEADER_BYTES], data[up.HEADER_BYTES:])

def send_message(file, data):
    with open(file, "wb") as f:
        f.write(data)

def write_json(file, js):
    with open(file, "w") as f:
        json.dump(js, f)