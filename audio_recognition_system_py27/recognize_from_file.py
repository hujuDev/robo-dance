#!/usr/bin/python
import sys
import numpy as np

import libs.fingerprint as fingerprint
import argparse

import soundfile as sf
import struct
import pyaudio
import wave
import os
from libs.reader_file import FileReader
from argparse import RawTextHelpFormatter
from itertools import izip_longest
from termcolor import colored
from libs.config import get_config
from libs.visualiser_console import VisualiserConsole as visual_peak
from libs.visualiser_plot import VisualiserPlot as visual_plot
from libs.db_sqlite import SqliteDatabase
from multiprocessing import Process
import io


# from libs.db_mongo import MongoDatabase

class FileRecognizer:
    def __init__(self, directory, fileName="out.wav", seconds=5):
        self.data = []
        self.directory = directory
        self.fileName = fileName
        self.filePath = self.directory + '/' + self.fileName
        self.seconds = seconds

    def grouper(self, iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return (filter(None, values) for values
                in izip_longest(fillvalue=fillvalue, *args))

    def return_matches(self, hashes, db):
        mapper = {}
        for hash, offset in hashes:
            mapper[hash.upper()] = offset
        values = mapper.keys()

        for split_values in self.grouper(values, 1000):
            # @todo move to db related files
            query = """
        SELECT upper(hash), song_fk, offset
        FROM fingerprints
        WHERE upper(hash) IN (%s)
      """
            query = query % ', '.join('?' * len(split_values))

            x = db.executeAll(query, split_values)
            matches_found = len(x)

            if matches_found > 0:
                msg = '   ** found %d hash matches (step %d/%d)'
                print colored(msg, 'green') % (
                    matches_found,
                    len(split_values),
                    len(values)
                )
            else:
                msg = '   ** not matches found (step %d/%d)'
                print colored(msg, 'red') % (
                    len(split_values),
                    len(values)
                )

            for hash, sid, offset in x:
                # (sid, db_offset - song_sampled_offset)
                yield (sid, offset - mapper[hash])

    def find_matches(self, samples, db, Fs=fingerprint.DEFAULT_FS):
        hashes = fingerprint.fingerprint(samples, Fs=Fs)
        return self.return_matches(hashes, db)

    def align_matches(self, matches, db):
        diff_counter = {}
        largest = 0
        largest_count = 0
        song_id = -1

        for tup in matches:
            sid, diff = tup

            if diff not in diff_counter:
                diff_counter[diff] = {}

            if sid not in diff_counter[diff]:
                diff_counter[diff][sid] = 0

            diff_counter[diff][sid] += 1

            if diff_counter[diff][sid] > largest_count:
                largest = diff
                largest_count = diff_counter[diff][sid]
                song_id = sid

        songM = db.get_song_by_id(song_id)

        nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                         fingerprint.DEFAULT_WINDOW_SIZE *
                         fingerprint.DEFAULT_OVERLAP_RATIO, 5)

        return {
            "SONG_ID": song_id,
            "SONG_NAME": songM[1],
            "CONFIDENCE": largest_count,
            "OFFSET": int(largest),
            "OFFSET_SECS": nseconds
        }

    def get_data_from_audio_file(self, filePath):
        seconds = 10
        filePath = self.directory + '/' + self.fileName
        print(filePath)

        fileReader = FileReader(filePath)
        song_info = fileReader.parse_audio(seconds)

        return song_info.get('channels')

    def get_data_from_audio_file_sf(self, filePath):
        # alternative approach to loading data as a stream using pyaudio
        data, samplerate = sf.read(filePath)
        return data

    def get_data_from_audio_file_pa(self, filePath):

        default_chunksize = 8192
        default_format = pyaudio.paInt16
        default_channels = 1
        default_rate = 44100
        default_seconds = 5

        data_output = [[] for i in range(default_channels)]

        wf = wave.open(filePath)
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        frames_per_buffer=default_chunksize,
                        output=True)

        bufferSize = int(default_rate / default_chunksize * default_seconds)

        for i in range(0, bufferSize):
            data = stream.read(default_chunksize)
            # A new 1-D array initialized from raw binary or text data in a string.
            nums = np.fromstring(data, np.int16)
            for c in range(default_channels):
                data_output[c].extend(nums[c::default_channels])

        return data_output

    def start(self):
        config = get_config()

        db = SqliteDatabase()

        chunksize = 2 ** 12  # 4096
        channels = 2  # int(config['channels']) # 1=mono, 2=stereo

        record_forever = False
        visualise_console = bool(config['mic.visualise_console'])
        visualise_plot = bool(config['mic.visualise_plot'])

        filePath = self.directory + '/' + self.fileName
        reader = FileReader(filePath)

        msg = ' * file has been read'
        print colored(msg, attrs=['dark'])

        # data = self.get_data_from_audio_file(self.filePath)
        data = self.get_data_from_audio_file_sf(filePath)
        # data = self.get_data_from_audio_file_pa(filePath)

        Fs = fingerprint.DEFAULT_FS
        channel_amount = len(data)

        result = set()
        matches = []

        for channeln, channel in enumerate(data):
            # TODO: Remove prints or change them into optional logging.
            msg = '   fingerprinting channel %d/%d'
            print colored(msg, attrs=['dark']) % (channeln + 1, channel_amount)

            matches.extend(self.find_matches(channel, db))

            msg = '   finished channel %d/%d, got %d hashes'
            print colored(msg, attrs=['dark']) % (
                channeln + 1, channel_amount, len(matches)
            )

        total_matches_found = len(matches)

        print ''

        if total_matches_found > 0:
            msg = ' ** totally found %d hash matches'
            print colored(msg, 'green') % total_matches_found

            song = self.align_matches(matches, db)

            msg = ' => song: %s (id=%d)\n'
            msg += '    offset: %d (%d secs)\n'
            msg += '    confidence: %d'

            print colored(msg, 'green') % (
                song['SONG_NAME'], song['SONG_ID'],
                song['OFFSET'], song['OFFSET_SECS'],
                song['CONFIDENCE']
            )
            return song
        else:
            msg = ' ** not matches found at all'
            print colored(msg, 'red')
            return None
