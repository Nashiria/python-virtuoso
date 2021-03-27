import datetime
import json
import os
import random

import librosa
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

import GenerateModel
import Play


def loadmodel(genre, insturment, trackfolder, modelpath):
    return GenerateModel.modelgenerate(genre, insturment, trackfolder=trackfolder, modelpath=modelpath)


def loadpatterns(genre, insturment):
    with open('data.txt') as json_file:
        database = json.load(json_file)
    database = database[genre]
    patterns = []
    for song in database:
        if insturment in database[song]["insturments"]:
            patterns.append(database[song]["insturments"][insturment]["pattern"])
    while [] in patterns:
        patterns.remove([])
    try:
        return patterns[0]
    except:
        print("There is not enough samples for this insturment")


def usePattern(model, genre, insturment):
    patterns = loadpatterns(genre, insturment)
    if len(patterns) == 0:
        patterns.append([1, 2, 3, 4, 1, 2, 3, 4])
        patterns.append([1, 2, 1, 2, 1, 2, 3, 4])
        patterns.append([1, 2, 3, 1, 2, 3, 1, 2, 1, 2, 1, 2, 3])
    currPattern = random.choice(patterns)
    currPattern2 = random.choice(patterns)
    currPattern = currPattern[0:round(len(currPattern) / 2)] + currPattern2[
                                                               round(len(currPattern2) / 2):len(currPattern2)]
    notecount = max(currPattern)
    usedNotes = []
    for _ in range(notecount + 1):
        if _ == 0:
            note1 = GenerateModel.randomnote(model)

            usedNotes.append(note1)
        else:
            note1 = GenerateModel.similarnote(model, usedNotes[_ - 1], 5)
            trytime = 0
            while note1 in usedNotes and trytime < 10:
                note1 = GenerateModel.similarnote(model, usedNotes[_ - 1], 5)
                trytime += 1
            usedNotes.append(note1)
    uniqueIndex = list(dict.fromkeys(currPattern))
    toReturn = []
    for note in currPattern:
        toReturn.append(usedNotes[uniqueIndex.index(note)])
    return toReturn


def namethefile(filetype):
    library = os.listdir("Generated")
    x = datetime.datetime.now()
    timestamp = "-" + str(x.day) + "-" + str(x.month) + "-" + str(x.year)
    recordid = 0
    for data in library:
        if (timestamp in data):
            recordid += 1
    return "Generated/" + filetype.capitalize() + timestamp + "-" + str(recordid) + ".mid"


def listtomidi(songl, tempo, filename, insturment):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    filename = filename.replace("Generated/", "")
    track.append(MetaMessage("marker", text=filename))
    track.append(MetaMessage("track_name", name="insturment"))
    i = 0
    import GenPlot
    while GenPlot.findinsturment(i) != insturment:
        i += 1
        if insturment == "Drums":
            i = 114
            break
        if i < 128:
            i = 1
            break

    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    track.append(
        MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8,
                    time=0))
    track.append(MetaMessage('key_signature', key="C", time=0))
    track.append(
        MetaMessage('smpte_offset', frame_rate=24, hours=32, minutes=0, seconds=0, frames=0, sub_frames=0, time=0))
    track.append(Message('program_change', program=i, time=0))
    bpm = (tempo) / (250000 / 240)
    lastnote = -1
    for part in songl:
        for notes in part:
            notelist = GenerateModel.notelisttransform(notes)[0]
            duration = int(round(100000 * notelist[1] / bpm)) * 3
            if duration == 0:
                duration = int(round(100000 * 0.5 / bpm)) * 3
            pause = (100000 / bpm) - duration
            if pause < 0:
                pause = 0
            for note in notelist[0]:
                if notelist[0].index(note) == 0:
                    time = int(pause)
                else:
                    time = 0
                track.append(
                    Message('note_on', note=librosa.note_to_midi(note.replace(".", "")), velocity=127, time=time))
                if lastnote != -1:
                    track.append(
                        Message('note_off', note=librosa.note_to_midi(lastnote), velocity=0, time=int(duration)))
                lastnote = note.replace(".", "")
            # time+=random.choice(durations)
    return mid


def partGen(genre, insturment, part="Intro", play=False, plot=False, speed=1, volume=1, tempo=120, trackfolder="tracks",
            modelpath="models"):
    part = part.lower()
    if part == "intro":
        pass
    if part == "outro":
        pass
    if part == "bridge":
        pass
    if part == "chorus":
        pass
    if part == "verse":
        pass
    if part == "outro":
        pass
    if part == "intro":
        pass

    start = datetime.datetime.now()
    model = loadmodel(genre, insturment, trackfolder=trackfolder, modelpath=modelpath)
    i = [usePattern(model=model, genre=genre, insturment=insturment) * 1]
    filename = namethefile(insturment.capitalize() + "-" + genre.capitalize())
    mid = listtomidi(i, round((250000 / 120) * tempo * 2), filename, insturment=insturment)
    mid.save(filename)
    gen = datetime.datetime.now() - start
    print("Generated", filename.replace("Generated/", ""), "in", str(gen))
    start = datetime.datetime.now()
    import Play, GenPlot
    if plot:
        try:
            GenPlot.showplotofmidi(filename, "GeneratedPlots/" + filename.replace("mid", "png"))
            plot = datetime.datetime.now() - start
            print("Ploted", filename, "in", str(plot))
        except:
            print("Plot failed.")
    if play:
        Play.play(filename, speed, volume)


def songGen(model, genre, insturment, play=False, plot=False, speed=1, volume=1, tempo=120):
    start = datetime.datetime.now()
    i = usePattern(model, genre, insturment) * 2
    # print("Generated Intro")
    v = usePattern(model, genre, insturment) * 2
    # print("Generated Verse")
    c = usePattern(model, genre, insturment) * 2
    # print("Generated Chorus")
    o = usePattern(model, genre, insturment) * 2
    # print("Generated Outro")
    b = usePattern(model, genre, insturment) * 2
    # print("Generated Bridge")
    structures = [
        [i, v, c, v, c, o],
        [i, v, c, v, c, b, v, c, o],
        [i, v, c, v, c, b, c, v, o],
        [i, c, v, c, v, b, c, o],
        [i, v, c, v, b, v, c, b, o]
    ]
    song_structure = random.choice(structures)
    songl = []
    for structure in song_structure:
        songl.append(structure)
    filename = namethefile("Song")
    mid = listtomidi(songl, round((250000 / 120) * tempo), filename)
    mid.save(filename)
    gen = datetime.datetime.now() - start
    print("Generated", filename.replace("Generated/", ""), "in", str(gen))
    start = datetime.datetime.now()
    import Play, GenPlot
    if plot:
        GenPlot.showplotofmidi(filename, "GeneratedPlots/" + filename.replace("mid", "png"))
        plot = datetime.datetime.now() - start
        print("Ploted", filename, "in", str(plot))
    if play:
        Play.play(filename, speed, volume)


def findinsturmentcategory(program):
    if program in range(0, 8):
        return "Piano"
    elif program in range(8, 16):
        return "Chromatic Percussion"
    elif program in range(16, 72):
        return "Organ"
    elif program in range(72, 80):
        return "Pipe"
    elif program in range(80, 88):
        return "Synth Lead"
    elif program in range(88, 96):
        return "Synth Pad"
    elif program in range(96, 104):
        return "Synth Effects"
    elif program in range(104, 112):
        return "Ethnic"
    elif program in range(112, 120):
        return "Percussive"
    elif program in range(120, 128):
        return "Sound Effects"
    else:
        return "Unknown"


def readmidi(filename, play=False, plot=False, printtracks=False):
    start = datetime.datetime.now()
    mid = mido.MidiFile(filename, clip=True)
    if printtracks:
        for track in mid.tracks:
            for message in track:
                print(message)
            print("\n\n\n")
    if play:
        Play.play(filename, 1, 1)
    if plot:
        import GenPlot
        GenPlot.showplotofmidi(filename, "GeneratedPlots/" + filename.replace("mid", "png").split("/")[-1])
        plot = datetime.datetime.now() - start
        print("Ploted", filename, "in", str(plot))


def get_files_by_file_size(directoryname, reverse=False):
    filepaths = []
    for basename in os.listdir(directoryname):
        filename = os.path.join(directoryname, basename)
        if os.path.isfile(filename):
            filepaths.append(filename)
    for i in range(len(filepaths)):
        filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))
    filepaths.sort(key=lambda filename: filename[1], reverse=reverse)
    for i in range(len(filepaths)):
        filepaths[i] = filepaths[i][0]
    return filepaths


def selectfromlist():
    list = get_files_by_file_size("models/", reverse=True)
    if "models/.DS_Store" in list:
        list.remove("models/.DS_Store")
    genres = {}
    for model in list:
        model = model.replace(".model", "").replace("models/", "").split("-")
        if model[0] not in genres:
            genres[model[0]] = []
        genres[model[0]].append(model[1])
    for genre in genres:
        print(genre)
    print("")
    genre = input("Genre:")
    for ins in genres[genre]:
        print(ins)
    print("")
    insturment = input("Insturment:")
    partGen(genre, insturment)


def notestomidi(notes=["C", "D", "C", "B"], reverb=False, volume=100, tempo=60, filename="ch0.wav",
                insturments=[0, 1, 2, 3, 4, 5], transpose="1", chord=[4, 6]):
    mid = MidiFile()
    notes.remove(notes[len(notes) - 1])
    notes.remove(notes[len(notes) - 1])
    channel = 0
    soundreverb = 1
    if reverb:
        soundreverb = 2
    for _ in range(soundreverb):
        for insturment in insturments:
            track = MidiTrack()
            mid.tracks.append(track)
            filename = filename.replace("Generated/", "")
            track.append(MetaMessage("marker", text=filename))
            track.append(MetaMessage("track_name", name=insturment))

            track.append(MetaMessage("instrument_name", name=insturment))
            track.append(Message("control_change", channel=channel, control=7,
                                 value=round((100 * (volume) / 127) + (100 * (volume / 5 * _) / 127)), time=0))
            MICROSECONDS_PER_MINUTE = 60000000
            MPQN = MICROSECONDS_PER_MINUTE / tempo
            track.append(MetaMessage('set_tempo', tempo=int(MPQN), time=0))

            track.append(Message('program_change', channel=channel, program=logicins(insturment), time=0))
            duration = int(480 / 500 * (MPQN * tempo / 60) / 2000)
            for notesx in notes:
                notesx = notesx.replace("9", "").replace("8", "").replace("7", "").replace("6", "").replace("5",
                                                                                                            "").replace(
                    "4", "").replace("3", "").replace("2", "").replace("1", "").replace("0", "").replace("-", "")
                note = librosa.note_to_midi(notesx + transpose)
                track.append(Message('note_on', note=note, velocity=127, time=0))
                for plus in chord:
                    track.append(Message('note_on', note=note + plus, velocity=127, time=0))
                track.append(Message('note_on', note=note, velocity=0, time=int(duration)))
                for plus in chord:
                    track.append(Message('note_on', note=note + plus, velocity=0, time=0))
            channel += 1
    mid.save(filename)
    return mid


def logicins(search):
    with open("insturments.txt", "r") as ins:
        ins = [x.replace("\n", "").replace("“", "").replace(",", "").replace("”", "") for x in ins]
        n = 0
        if search in ins:
            return ins.index(search)
        else:
            return 0


def returnchords(key):
    if key == "Major":
        return [4, 7]
    if key == "Minor":
        return [3, 7]
    if key == "Suspended fourth":
        return [5, 7]
    if key == "Power chord":
        return [7]
    if key == "Major seventh":
        return [4, 7, 11]
    if key == "Minor seventh":
        return [3, 7, 10]
    if key == "Dominant seventh":
        return [4, 7, 10]
    if key == "Diminished seventh":
        return [3, 6, 9]
    if key == "Add 6":
        return [4, 7, 9]
    if key == "Add 9":
        return [4, 7, 14]
    if key == "6/9":
        return [4, 7, 9, 14]
    if key == "Dominant ninth":
        return [4, 7, 10, 14]
    else:
        return []


def background(filename, tempo=60, volume=100, reverb=False, transpose=2, chords="no", insturments=["Hard Rock"]):
    import Background
    notes = Background.filetonotes(filename, tempo)
    notestomidi(notes=notes, reverb=reverb, volume=volume, tempo=tempo, transpose=str(transpose),
                filename=filename.replace(".m4a", ".mid").replace("wav", "mid"), chord=returnchords(chords),
                insturments=insturments)


chord = "Power chord"
usedInsturments = ["Hard Rock"]
background("Output 1-2-AAC.wav", volume=30, reverb=True, tempo=15, transpose=2, chords=chord,
           insturments=usedInsturments)
