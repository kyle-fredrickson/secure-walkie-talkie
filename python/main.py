import argparse
import getpass
import json
import os
import subprocess
import sys

sys.path.append("src")
import Audio as aud
import CounterMode as cm
from TcpListener import TcpListener
import SHA3 as hash
from TcpTalker import TcpTalker
import UtilityConfig as uc

### Setup ###

NONCE_BYTES = 8

try:
    RECORDING_PATH = "recording"
    AUDIO = aud.Audio(RECORDING_PATH)
except:
    print("Error: audio setup failed")

### Functionality ###

def login(name, debug = False):
    file_name = os.path.join("config", name + ".json")
    with open(file_name, "rb") as file:
        config = file.read()

    js = json.loads(config)
    config = uc.UtilityConfig(js)

    return config

    """
    if not debug:
        password = getpass.getpass(name + ", enter your password:")

        (k, nonce) = hash.sha3_512_split(password.encode())
        nonce = int(nonce[: 2 * NONCE_BYTES], 16)

        file_name = os.path.join("config", name + ".encrypted")
        with open(file_name, "rb") as file:
            enc_config = file.read()

        c = cm.CounterMode(k)

        config = c.decrypt(enc_config, nonce).decode("utf-8").replace(" ", "").replace("\n", "")
        js = json.loads(config)

        config = uc.UtilityConfig(js)
        return config
    else:
        file_name = os.path.join("config", name + ".json")
        with open(file_name, "rb") as file:
            config = file.read()

        js = json.loads(config)
        config = uc.UtilityConfig(js)

        return config
    """

def listen(config, text):
    try:
        l = TcpListener(config)
        data = l.listen()

        if text:
            print(data.decode("utf-8"))
        else:
            AUDIO.play(data)

    except Exception as e:
        print(str(e))

def talk(file, name, config, text):
    try:
        t = TcpTalker(config, name)

        if text:
            data = file.encode()
        else:
            data = AUDIO.read(file)

        t.talk(data)
    except Exception as e:
        print(str(e))
        #print("Error: sending failed")

def record(n, file):
    try:
        saved = AUDIO.record(n, file)

        d = AUDIO.read(saved)
        AUDIO.play(d)
    except:
        print("Error: could not record and save")

def play(file):
    try:
        print("Playing:", os.path.join(os.getcwd(), RECORDING_PATH, file))
        AUDIO.playFile(file)
    except Exception as e:
        print("Error: could not play", os.path.join(os.getcwd(), RECORDING_PATH, file))
        print(str(e))

def listcontacts(config):
    try:
        contacts = "Contacts:\n"
        for i in config.get_contacts():
            contacts = contacts + "\t-" + i
        print(contacts)
    except:
        print("Error: could not display contacts")

def openconfig():
    try:
        print("Opening configuration:", os.path.join(os.getcwd(), CONFIG_PATH))
        subprocess.run(['open', CONFIG_PATH], check=True)
    except:
        print("Error: could not open config")

def main():
    parser = argparse.ArgumentParser(description="Securely send voice over TCP!")

    parser.add_argument("-d", "--debug", action = "store_true", help="use in debug mode with plaintext configs")
    parser.add_argument("--login", metavar = ("NAME"), nargs = 1, help = "Load NAME using PASSWORD")
    parser.add_argument("--text", action = "store_true", help="process text")


    group = parser.add_mutually_exclusive_group()

    group.add_argument("-l", "--listen", action = "store_true", help = "listen for connections")
    group.add_argument("-t", "--talk", metavar = ("FILE", "NAME"), nargs = 2, help = "send FILE to NAME of contact")

    group.add_argument("-r", "--record", metavar = ("N", "FILE"), nargs = 2, help = "record N seconds of audio to FILE")
    group.add_argument("-p", "--play", metavar = ("FILE"), nargs = 1, help = "play FILE")

    group.add_argument("-lc", "--listcontacts", action = "store_true", help = "lists all contacts")

    args = parser.parse_args()

    try:
        config = login(args.login[0], args.debug)
        print("You're in, " + args.login[0] + "!\n")

        if args.listen:
            print("Listening...\n")
            listen(config, args.text)
        elif args.talk:
            print("Sending...\n")
            talk(args.talk[0], args.talk[1], config, args.text)
        elif args.record:
            print("Recording...\n")
            record(int(args.record[0]), args.record[1])
        elif args.play:
            play(args.play[0])
        if args.listcontacts:
            listcontacts(config)
    except:
        print("An error occured, \"" + args.login[0] + "\"")

if __name__ == "__main__":
    """password = getpass.getpass("enter your password:")

    (k, nonce) = hash.sha3_512_split(password.encode())
    nonce = int(nonce[: 2 * NONCE_BYTES], 16)

    with open("config/Bob.json", "rb") as inf:
        pt = inf.read()

    print(type(pt))

    pt = pt.decode("utf-8").replace(" ", "").replace("\n", "").encode()

    c = cm.CounterMode(k)
    ct = c.encrypt(pt, nonce)

    with open("config/Bob.encrypted", "wb") as outf:
        outf.write(ct)"""

    
    main()
