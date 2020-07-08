#!/usr/bin/env python3

import argparse
import getpass
import json
import os
import subprocess
import sys

sys.path.append("src")

import UtilityConfig as uc
import UtilityProtocol2 as p

def send_request(config, vars)

def setup(step, config, vars):
    if step == "1":
        send_request(config, vars)
    elif step == "2":
        send_request(config, vars)
    elif step == "3":
        send_request(config, vars)
    elif step == "D":
        send_request(config, vars)
    else:
        print("Invalid message type.")

    return ("wow", "cool")

def main():
    parser = argparse.ArgumentParser(description="Test script for interoperability!")

    parser.add_argument("config", nargs = 1, help = "Where's your config?")
    parser.add_argument("vars", nargs = 1, help = "Where are your local vars?")
    parser.add_argument("step", nargs = 1, help="What stage of the interchange are we at?")
    parser.add_argument("-s", action = "store_true", help = "Use this tag to send, else you will receive.")
    parser.add_argument("--message", nargs = 1, help = "Where is the message you\'re going to process")

    args = parser.parse_args()

    step = args.step[0]
    config = uc.UtilityConfig(args.config[0])
    vars = args.vars[0]

    if args.message:
        message = args.message[0]
        (out, var_out) = setup(step, config, vars, message)
    else:
        (out, var_out) = setup(step, config, vars)

if __name__ == "__main__":
    main()
