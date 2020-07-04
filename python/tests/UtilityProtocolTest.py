import json
import sys

sys.path.append('../src/')
import UtilityProtocol as up
import UtilityConfig as uc

def main():
    rand = up.generate_random_key()
    print("generate_random_key passed:", int(rand, 16) != None and len(rand) == 64)

    print(rand)


if __name__ == "__main__":
    main()
