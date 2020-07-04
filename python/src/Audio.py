import datetime
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
import pydub.playback as pd
import os
#from playsound import playsound

class Audio:
    sample_rate = 44100

    def __init__(self, dir):
        self.directory = dir

    def play(self, data):
        file = self.write(data)
        self.playFile(file)
        #os.remove(os.path.join(self.directory, file + ".wav"))

    # Plays the file at file
    # play: str -> void (plays file)
    def playFile(self, file):
        full_file = os.path.join(self.directory, file + ".wav")
        sound = AudioSegment.from_wav(full_file)
        pd.play(sound)

    # Records 'sec' seconds of audio and saves to dir/file
    # record: int, str -> the relative file name
    def record(self, sec, file):
        full_file = os.path.join(self.directory,file + ".wav")

        recording = sd.rec(int(sec * Audio.sample_rate), samplerate= Audio.sample_rate, channels=1)
        sd.wait()

        write(full_file, Audio.sample_rate, recording)

        print("Saved:", os.path.join(os.getcwd(), full_file))

        return file


    # Doesn't work vvv
    # (or at least it's implicated in something that doesn't work)
    def read(self, file):
        full_file = os.path.join(self.directory,file + ".wav")

        with open(full_file, "rb") as in_file:
            data = in_file.read()

        return data

    # Write binary data to now!
    def write(self, data):
        file = str(datetime.datetime.now())
        full_file = os.path.join(self.directory, file + ".wav")

        with open(full_file, "wb") as out_file:
            out_file.write(data)

        return file
