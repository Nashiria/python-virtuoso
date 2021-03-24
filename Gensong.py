import datetime
import json
import os
import random
import mido
import librosa
from mido import Message, MidiFile, MidiTrack, MetaMessage

import GenerateModel
import Play
def loadmodel(genre,insturment,trackfolder,modelpath):
    return GenerateModel.modelgenerate(genre,insturment ,trackfolder=trackfolder,modelpath=modelpath)
def loadpatterns(genre,insturment):
    with open('data.txt') as json_file:
        database = json.load(json_file)
    database=database[genre]
    patterns=[]
    for song in database:
        if insturment in database[song]["insturments"]:
            patterns.append(database[song]["insturments"][insturment]["pattern"])
    while [] in patterns:
        patterns.remove([])
    return patterns[0]
def usePattern(model,genre,insturment):
    patterns=loadpatterns(genre,insturment)
    if len(patterns)==0:
        patterns.append([1,2,3,4,1,2,3,4])
        patterns.append([1,2,1,2,1,2,3,4])
        patterns.append([1,2,3,1,2,3,1,2,1,2,1,2,3])
    currPattern = random.choice(patterns)
    currPattern2 = random.choice(patterns)
    currPattern = currPattern[0:round(len(currPattern) / 2)] + currPattern2[round(len(currPattern2) / 2):len(currPattern2)]
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


def listtomidi(songl, tempo, filename,insturment):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    filename = filename.replace("Generated/", "")
    track.append(MetaMessage("marker", text=filename))
    track.append(MetaMessage("track_name", name="insturment"))
    i=0
    import GenPlot
    while GenPlot.findinsturment(i)!=insturment:
        i+=1
        if insturment=="Drums":
            i=114
            break
        if i<128:
            i=1
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
            duration=int(round(100000*notelist[1]/bpm))
            if duration==0:
                duration = int(round(100000 * 0.5 / bpm))
            for note in notelist[0]:
                track.append(Message('note_on', note=librosa.note_to_midi(note.replace(".","")), velocity=127, time=int(duration)))
                if lastnote != -1:
                    track.append(Message('note_off', note=librosa.note_to_midi(lastnote), velocity=0, time=int(duration)))
                lastnote = note.replace(".","")
            # time+=random.choice(durations)
    return mid


def partGen(genre,insturment,part="Intro", play=False, plot=False, speed=1, volume=1, tempo=120,trackfolder="tracks",modelpath="models"):
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
    model=loadmodel(genre,insturment,trackfolder=trackfolder,modelpath=modelpath)
    i = [usePattern(model=model,genre=genre,insturment=insturment) * 1]
    filename = namethefile(insturment.capitalize()+"-"+genre.capitalize())
    mid = listtomidi(i, round((250000 / 120) * tempo), filename,insturment=insturment)
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


def songGen(model,genre,insturment,play=False, plot=False, speed=1, volume=1, tempo=120):
    start = datetime.datetime.now()
    i = usePattern(model,genre,insturment) * 2
    # print("Generated Intro")
    v = usePattern(model,genre,insturment) * 2
    # print("Generated Verse")
    c = usePattern(model,genre,insturment) * 2
    # print("Generated Chorus")
    o = usePattern(model,genre,insturment) * 2
    # print("Generated Outro")
    b =usePattern(model,genre,insturment) * 2
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
    if program in range(0,8):
        return "Piano"
    elif program in range(8,16):
        return "Chromatic Percussion"
    elif program in range(16,72):
        return "Organ"
    elif program in range(72,80):
        return "Pipe"
    elif program in range(80,88):
        return "Synth Lead"
    elif program in range(88,96):
        return "Synth Pad"
    elif program in range(96,104):
        return "Synth Effects"
    elif program in range(104,112):
        return "Ethnic"
    elif program in range(112,120):
        return "Percussive"
    elif program in range(120,128):
        return "Sound Effects"
    else:
        return "Unknown"

def readmidi(filename,play=False,plot=False,printtracks=False):
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


partGen("Rock","Acoustic Guitar (steel)")