import audioop
import os
from hashlib import sha1

import numpy as np
import pyaudio
import numpy
import wave

from pydub import AudioSegment

from reader import BaseReader


class FileReader(BaseReader):
    default_chunksize = 8192
    default_format = pyaudio.paInt16
    default_channels = 1
    default_rate = 16000
    default_seconds = 5

    # set default
    def __init__(self, filepath):
        super(FileReader, self).__init__("")
        self.filepath = filepath
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.data = []
        self.channels = FileReader.default_channels
        self.chunksize = FileReader.default_chunksize
        self.rate = FileReader.default_rate
        self.recorded = False

    def parse_audio(self, limit=None):

        songname, extension = os.path.splitext(os.path.basename(self.filepath))

        try:
            audiofile = AudioSegment.from_file(self.filepath)

            if limit:
                audiofile = audiofile[:limit * 1000]

            data = np.fromstring(audiofile._data, np.int16)

            channels = []
            for chn in xrange(audiofile.channels):
                channels.append(data[chn::audiofile.channels])

            fs = audiofile.frame_rate
        except audioop.error:
            print('audioop.error')

        return {
            "songname": songname,
            "extension": extension,
            "channels": channels,
            "Fs": audiofile.frame_rate,
            "file_hash": self.parse_file_hash()
        }

    def parse_file_hash(self, blocksize=2 ** 20):
        """ Small function to generate a hash to uniquely generate
        a file. Inspired by MD5 version here:
        http://stackoverflow.com/a/1131255/712997

        Works with large files.
        """
        s = sha1()

        with open(self.filepath, "rb") as f:
            while True:
                buf = f.read(blocksize)
                if not buf: break
                s.update(buf)

        return s.hexdigest().upper()

    def start_recording(self, channels=default_channels,
                        rate=default_rate,
                        chunksize=default_chunksize,
                        seconds=default_seconds):
        self.chunksize = chunksize
        self.channels = channels
        self.recorded = False
        self.rate = rate

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = self.audio.open(
            format=self.default_format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunksize,
        )

        self.data = [[] for i in range(channels)]

    def read_data_from_file(self, filepath, channels):

        fileReader = FileReader()
        self.data = [[] for i in range(channels)]

    def process_recording(self):
        data = self.stream.read(self.chunksize)

        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.fromstring.html
        # A new 1-D array initialized from raw binary or text data in a string.
        nums = numpy.fromstring(data, numpy.int16)

        for c in range(self.channels):
            self.data[c].extend(nums[c::self.channels])
            # self.data[c].append(data)

        return nums

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.recorded = True

    def get_recorded_data(self):
        with open(self.filepath, "rb") as inp_f:
            self.data = inp_f.read()
        return self.data

    def save_recorded(self, output_filename):
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.default_format))
        wf.setframerate(self.rate)

        # values = ','.join(str(v) for v in self.data[1])
        # numpydata = numpy.hstack(self.data[1])

        chunk_length = len(self.data[0]) / self.channels
        result = numpy.reshape(self.data[0], (chunk_length, self.channels))
        # wf.writeframes(b''.join(numpydata))
        wf.writeframes(result)
        wf.close()

    def play(self):
        pass

    def get_recorded_time(self):
        return len(self.data[0]) / self.rate
