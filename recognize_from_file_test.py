from audio_recognition_system_py27.recognize_from_file import FileRecognizer
import sys
import os

sys.path.insert(0, './audio_recognition_system_py27/libs')


def main():
    fileRecognizer = FileRecognizer(os.getcwd())
    fileRecognizer = FileRecognizer(os.getcwd(), "disco_disco.mp3")
    # fileRecognizer = FileRecognizer(os.getcwd(), "disco_disco2.mp3")
    # fileRecognizer = FileRecognizer(os.getcwd(), "out2.wav")
    # fileRecognizer = FileRecognizer(os.getcwd(), "test.wav")
    song_info = fileRecognizer.start()


if __name__ == '__main__':
    main()
