#!/usr/bin/env python3

import argparse
import json
import sys

sys.path.append("../python/src")
import FileTalker as ft
import UtilityConfig as uc

def talk(config, recipient, message, type, infile, outfile, vars):
    talker = ft.FileTalker(config, recipient, infile, outfile, vars)
    talker.talk(message, type)

def main():
    parser = argparse.ArgumentParser(description = "Securely send messages via files")
    parser.add_argument("config", nargs = 1, help="The config to use.")
    parser.add_argument("recipient", nargs = 1, help="Who to send to.")
    parser.add_argument("message", nargs = 1, help="The message")
    parser.add_argument("type", nargs = 1, help="The message type")
    parser.add_argument("infile", nargs = 1, help="The file to process.")
    parser.add_argument("outfile", nargs = 1, help="The file to write to.")
    parser.add_argument("vars", nargs = 1, help="The file to write previous vars to.")

    args = parser.parse_args()

    config = uc.UtilityConfig(args.config[0])
    recipient = args.recipient[0]
    message = args.message[0].encode()
    type = args.type[0]
    infile = args.infile[0]
    outfile = args.outfile[0]
    vars = args.vars[0]

    talk(config, recipient, message, type, infile, outfile, vars)

if (__name__ == "__main__"):
    main()