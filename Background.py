import struct
import wave

import librosa
import numpy as np


def seperatechannels(fn):
    wav = wave.open(fn)
    for channel in range(1):
        nch = wav.getnchannels()
        depth = wav.getsampwidth()
        wav.setpos(0)
        sdata = wav.readframes(wav.getnframes())
        typ = {1: np.uint8, 2: np.uint16, 4: np.uint32}.get(depth)
        data = np.fromstring(sdata, dtype=typ)
        ch_data = data[channel::nch]
        outwav = wave.open("ch" + str(channel) + ".wav", 'w')
        outwav.setparams(wav.getparams())
        outwav.setnchannels(1)
        outwav.writeframes(ch_data.tostring())
        outwav.close()


def tonotes(filename, tempo=120):
    array = []
    notes = []
    nots = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "G", "G#"]
    octaves = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    for note in nots:
        for oct in octaves:
            notes.append(note + oct)
    for note in notes:
        array.append(librosa.note_to_hz(note))
    window_size = int(2205 * 4 * (60 / int(tempo)))
    sampling_freq = 44100
    threshold = 600
    Identified_Notes = []
    sound_file = wave.open(filename, 'r')
    file_length = sound_file.getnframes()
    sound = np.zeros(file_length)
    for i in range(file_length):
        data = sound_file.readframes(1)
        data = struct.unpack("<h", data)
        sound[i] = int(data[0])
    sound = np.divide(sound, float(2 ** 15))
    sound_square = np.square(sound)
    frequency = []
    i = 0
    k = 0
    while (i <= len(sound_square) - window_size):
        s = 0.0
        j = 0
        while (j <= window_size):
            s = s + sound_square[i + j - 1]
            j = j + 1
        if s < threshold:
            if (i - k > window_size * 4):
                dft = np.fft.fft(sound[k:i])
                dft = np.argsort(dft)
                if (dft[0] > dft[-1] and dft[1] > dft[-1]):
                    i_max = dft[-1]
                elif (dft[1] > dft[0] and dft[-1] > dft[0]):
                    i_max = dft[0]
                else:
                    i_max = dft[1]
                frequency.append((i_max * sampling_freq) / (i - k))
                k = i + 1
        i = i + window_size
    for i in frequency:
        idx = (np.abs(array - i)).argmin()
        Identified_Notes.append(notes[idx])
    return Identified_Notes


def filetonotes(filename, tempo):
    seperatechannels(filename)
    notes = tonotes("ch0.wav", tempo=tempo)
    return notes
