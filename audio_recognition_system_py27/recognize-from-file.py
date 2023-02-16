import os
from libs.reader_file import FileReader

def recognize_from_file(fileName = "disco_disco.mp3"):
    seconds = 5
    # fileName = "awaken-136824.mp3"

    directory = os.getcwd()
    filePath = directory + '/mp3/' + fileName
    print(filePath)

    r = FileReader(filePath)
    song_info = r.parse_audio(seconds)
    r.recognize()

    print(song_info.get('songname'))
    return song_info

recognize_from_file()
