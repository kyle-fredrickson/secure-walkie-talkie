import sys

sys.path.append('../src/')
from Audio import Audio

def main():
    a = Audio("../recording/")
    print("Recording...")
    a.record(5, "../recording/test")
    print("Playing...")
    a.playFile("test.wav")


if __name__ == "__main__":
    main()
