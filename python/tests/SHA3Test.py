import sys

sys.path.append('../src/')
import SHA3

def main():
    m = "this is a random string of bytes that will go into the very cool sha3 hashing algorithm. really hash algorithms are astonishing-- they're not one-to-one but practically they behave that way. what a cool application that is emblamatic of computer science as a discipline which sits at the corner of practical applications and theory. amazing."
    m = m.encode()
    (x,y) = SHA3.sha3_512_split(m)
    hash = SHA3.sha3_512(m)
    print("SHA3_512_split passed:", x + y == hash and len(x) == len(y))

if __name__ == "__main__":
    main()
