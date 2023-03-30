import os

import abracadabra.recognise
import abracadabra.fingerprint
import abracadabra.storage
import sys


def setup():
    abracadabra.storage.setup_db()
    # loop over files in mp3 directory and register all new songs
    dir = "song_db"
    for filename in os.listdir(dir):
        if filename.endswith(".mp3") and not abracadabra.recognise.song_in_db(dir + "/" + filename):
            abracadabra.recognise.register_song(dir + "/" + filename)

def resetup():
    abracadabra.storage.drop_tables()
    setup()


def list_songs():
    # iterate over all songs in db and print them
    for song in abracadabra.storage.list_songs():
        print(song[-2] + ": ", song)


def recognise(filename):
    # get current working directory
    directory = os.getcwd()
    # filepath = os.path.join(directory, "recordings", filename)
    filepath = os.path.join(directory, filename)
    if (abracadabra.recognise.recognise_song(filepath) == None):
        print("None")
        print(1)
    else:
        print(abracadabra.recognise.recognise_song(filepath)[-2])
        print(abracadabra.recognise.recognise_song(filepath)[-1])


if __name__ == '__main__':
    # Get the name of the function to be called from the command-line argument
    function_name = sys.argv[1]
    func = getattr(sys.modules[__name__], function_name)
    args = sys.argv[2:]

    # Check if any arguments were passed and set default values if not
    func(*args)
