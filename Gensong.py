import datetime
import json
import os
import random
import Plot

from mido import Message, MidiFile, MidiTrack, MetaMessage

import GenerateModel
import Play

model = GenerateModel.modelgenerate("midimodel", "tracks")


def usePattern():
    if "patterns.json" in os.listdir():
        with open('patterns.json', 'r') as outfile:
            patterns = json.load(outfile)
            patterns = patterns["patterns"]
    else:
        import Pattern
        with open('patterns.json', 'w') as outfile:
            json.dump(Pattern.PatternAppend(), outfile)
        with open('patterns.json', 'r') as outfile:
            patterns = json.load(outfile)
            patterns = patterns["patterns"]
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


def listtomidi(songl, tempo):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    track.append(
        MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8,
                    time=0))
    track.append(MetaMessage('key_signature', key="C", time=0))
    track.append(
        MetaMessage('smpte_offset', frame_rate=24, hours=32, minutes=0, seconds=0, frames=0, sub_frames=0, time=0))
    track.append(Message('program_change', program=1, time=0))
    bpm = (tempo*3) / (250000 / 120)
    birtam = 60 * (32 * 1)
    notalar = [
        60 * 32 * 1 * 120 / bpm,
        60 * 32 * (1 / 2) * 120 / bpm,
        60 * 32 * (1 / 4) * 120 / bpm,
        # 60*32*(1/8)*120/bpm,
        # 60*32*(1/16)*120/bpm,
        # 60*32*(1/32)*120/bpm,
        # 60*32*(1/64)*120/bpm,

    ]

    lastnote = -1
    for part in songl:
        for notes in part:
            notelist = GenerateModel.notetomidivalue2(notes)
            for note in notelist:
                duration = random.choice(notalar)
                track.append(Message('note_on', note=note, velocity=127, time=round(duration)))
                if lastnote != -1:
                    track.append(Message('note_off', note=lastnote, velocity=0, time=round(duration / 2)))
                lastnote = note
            # time+=random.choice(durations)
    return mid


def partGen(part="Intro", play=False, plot=False, speed=1, volume=1, tempo=120):
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
    i = [usePattern() * 1]
    filename = namethefile(part)
    mid = listtomidi(i, round((250000 / 120) * tempo))
    mid.save(filename)
    gen = datetime.datetime.now() - start
    print("Generated", filename.replace("Generated/", ""), "in", str(gen))
    start = datetime.datetime.now()
    import Play, Plot
    if plot:
        try:
            Plot.showplotofmidi(filename, "GeneratedPlots/" + filename.replace("mid", "png"))
            plot = datetime.datetime.now() - start
            print("Ploted", filename, "in", str(plot))
        except:
            print("Plot failed.")
    if play:
        Play.play(filename, speed, volume)



def songGen(play=False, plot=False, speed=1, volume=1,tempo=120):
    start = datetime.datetime.now()
    i = usePattern() * 2
    # print("Generated Intro")
    v = usePattern() * 2
    # print("Generated Verse")
    c = usePattern() * 2
    # print("Generated Chorus")
    o = usePattern() * 2
    # print("Generated Outro")
    b = usePattern() * 2
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
    mid = listtomidi(songl, round((250000 / 120) * tempo))
    mid.save(filename)
    gen = datetime.datetime.now() - start
    print("Generated", filename.replace("Generated/", ""), "in", str(gen))
    start = datetime.datetime.now()
    import Play, Plot
    if plot:
        Plot.showplotofmidi(filename, "GeneratedPlots/" + filename.replace("mid", "png"))
        plot = datetime.datetime.now() - start
        print("Ploted", filename, "in", str(plot))
    if play:
        Play.play(filename, speed, volume)



def readmidi(filename):
    mid = MidiFile(filename, clip=True)

    start = datetime.datetime.now()
    Play.play(filename, 1, 1)
    for message in mid.tracks[0]:
        print(message)
    try:
        Plot.showplotofmidi(filename, "GeneratedPlots/" + filename.replace("mid", "png").split("/")[-1])
        plot = datetime.datetime.now() - start
        print("Ploted", filename, "in", str(plot))
    except:
        print("Plotting failed.")


#readmidi("Generated/Intro-22-3-2021-0.mid")
songGen(play=True, plot=True, tempo=120)
