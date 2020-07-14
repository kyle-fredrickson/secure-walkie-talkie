#!/usr/bin/env python3

import argparse
import sys

sys.path.append("../python/src")
import FileListener as fl
import UtilityConfig as uc

def listen(config, type, infile, outfile, vars):
    listener = fl.FileListener(config, infile, outfile, vars)
    return listener.listen(type)

def main():
    parser = argparse.ArgumentParser(description = "Securely send messages via files")
    parser.add_argument("config", nargs = 1, help="The config to use.")
    parser.add_argument("type", nargs = 1, help="The message type")
    parser.add_argument("infile", nargs = 1, help="The file to process.")
    parser.add_argument("outfile", nargs = 1, help="The file to write to.")
    parser.add_argument("vars", nargs = 1, help="The file to write previous vars to.")

    args = parser.parse_args()

    config = uc.UtilityConfig(args.config[0])
    type = args.type[0]
    infile = args.infile[0]
    outfile = args.outfile[0]
    vars = args.vars[0]

    message = listen(config, type, infile, outfile, vars)
    
    if type == "3":
        print(message)

if (__name__ == "__main__"):
    main()