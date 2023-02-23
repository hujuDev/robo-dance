import os
from libs.reader_file import FileReader

def recognize_from_file(fileName = "out.wav"):
    seconds = 7
    fileName = "disco_disco.mp3"
    # fileName = "awaken-136824.mp3"

    directory = os.getcwd()
    filePath = directory + '/' + fileName
    print(filePath)

    r = FileReader(filePath)
    song_info = r.parse_audio(seconds)
    r.recognize()

    print(song_info.get('songname'))
    print(song_info.get('file_hash'))
    return song_info
# hash out: '59A7FEA7FD9B66CF9BB790F6A1FB3A25C69479F8'
# hash out: 'A1A52535BDFB130E382420B4E7583140F3AB01F7'

# recognize_from_file()

def main():
    recognize_from_file()


if __name__ == "__main__":
    main()
