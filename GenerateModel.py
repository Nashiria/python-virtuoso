import music21 as md
import os
import random
import gensim,librosa,GenPlot,mido,datetime

import numpy as np
def trackPattern(notetext):
    allthetext = notetext.replace(".", "").replace("x", "")
    allthetext = allthetext.replace(" ", "-")
    allthetextList = allthetext.split("-")
    nwlist=[]
    for part in allthetextList:
        part=part.split("w")
        part=part[0]
        nwlist.append(part)
    allthetextList=nwlist
    currentPattern = ""
    allthetext="-".join(allthetextList)
    allpatterns = []
    for note in allthetextList:
        currentPattern += note + "-"
        if allthetext.count(currentPattern) > 2:
            pass
        else:
            allpatterns.append(currentPattern)
            currentPattern = ""
    mylist = list(dict.fromkeys(allpatterns))
    final = []
    for pat in mylist:
        x = pat.split("-")
        if "" in x:
            x.remove("")
        if len(x) > 8:
            final.append(x)
    v = []
    for pattern in final:
        patternnotes = list(dict.fromkeys(pattern))
        temp = []
        for note in pattern:
            temp.append(patternnotes.index(note))
        v.append(temp)
    return v


def miditosentences(trackname):
    file = md.converter.parse(trackname)

    partStream = file.parts.stream()
    mf = md.midi.translate.streamToMidiFile(partStream)
    f=md.instrument.partitionByInstrument(file)
    alltracks = {}
    for _ in f:
        ins=str(_).replace("<music21.stream.Part ","").replace(">","")
        notes = []
        for n in _.flat.notes:
            if "<music21.note." in str(n):
                note = str(n.pitch.name).replace("B-", "A#").replace("E-", "D#").replace("A-", "G#").replace("G-",
                                                                                                             "F#").replace(
                    "D-", "C#")
                notes.append([note + "" + str(n.pitch.octave), n.quarterLength])
            if "<music21.chord.Chord" in str(n):
                chord = []
                for note in n.pitches:
                    note = str(note).replace("B-", "A#").replace("E-", "D#").replace("A-", "G#").replace("G-",
                                                                                                         "F#").replace("D-",
                                                                                                                       "C#")

                    note = note.replace("(<music21.pitch.Pitch ", "").replace(">,", "")
                    chord.append(note)
                chord = str(chord).replace("[", "").replace("'", "").replace(",", "").replace("]", "")
                notes.append([chord, n.quarterLength])
        ctmp = 0
        data = ""
        for note in notes:
            duration = note[1]
            duration=str(duration)
            key=note[0]
            data+="x".join(key.split(" "))+"x"+duration.replace(".","p").replace("/","s")+" "

        x=0
        if ins in alltracks:
            alltracks[ins].append(data[:-1])
        else:
            alltracks[ins]=[]
            alltracks[ins].append(data[:-1])
    return alltracks

def evaluatedata(alldata,filename,modelpath):
    words=alldata.split(" ")
    sentences=[]
    for _ in range(len(words)):
        group=[]
        try:
            group.append(words[_])
        except:
            pass
        try:
            group.append(words[_+1])
        except:
            pass
        try:
            group.append(words[_+2])
        except:
            pass
        try:
            group.append(words[_+3])
        except:
            pass
        sentences.append(" ".join(group))
    nwlist = []
    for sentence in sentences:
        v = str(sentence)
        v = v.split(" ")
        sentence = v
        if "" in sentence:
            sentence.remove("")
        nwlist.append(sentence)
    sentences = nwlist
    model = gensim.models.Word2Vec(sentences,min_count=1, size=500)
    model.train(sentences, total_examples=len(sentences), epochs=100)
    model.init_sims(replace=True)
    model.save(modelpath+"/"+filename)
    return model
def sentencealltracks(tracklist):
    data = ""
    if len(tracklist)!=0:
        for trackname in tracklist:
            text = miditosentences2(trackname)
            data += text
    return data
def notetomidivalue(note):
    str = ""
    lx = []
    if len(note) < 4:
        note = [note]
    else:
        for char in note:
            if char in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0"]:
                char=char.replace("1","2").replace("0","2").replace("6","5").replace("7","5").replace("8","5")
                str += char
                lx.append(str)
                str = ""
            else:
                str += char
    return librosa.note_to_midi(lx)
def notelisttransform(notelist):
        toReturn=[]
        note=notelist.split("w")
        duration=note[1]
        notes=note[0].split("x")
        if "p" in duration:
            duration=duration.split("p")
            duration=int(duration[0])+int(duration[1])/len(duration[1]*10)
        elif "s" in duration:
            duration = duration.split("s")
            duration=int(duration[0])/int(duration[1])
        toReturn.append([notes,duration])
        return toReturn

def modelgenerate(genre,insturment ,trackfolder="tracks",modelpath="models"):
    import json
    filename = genre+"-"+insturment + ".model"
    filenamepath = "./models/" + filename
    if (os.path.isfile(filenamepath)):  # if there is a model saved, load it
        model = gensim.models.Word2Vec.load(filenamepath)
    else:
            midilist = []
            if "data.txt" in os.listdir():
                pass
            else:
                trackstojson(trackfolder)
            with open('data.txt') as json_file:
                database = json.load(json_file)
            text=[]
            for song in database[genre]:
                try:
                    text.append(database[genre][song]["insturments"][insturment]["notes"])
                except:
                    pass
            allthetext=".".join(text)
            model = evaluatedata(allthetext,filename,modelpath=modelpath)
    return model
def randomnote(model):
    return random.choice(model.wv.index2entity)
def similarnote(model, note, count):
    v = model.wv.similar_by_word(note, topn=count)
    v = random.choice(v)
    v = v[0]
    return v
def notetomidivalue(note):
    notenum = []
    str = ""
    lx = []
    if len(note) < 4:
        note = [note]
    else:
        for char in note:
            if char in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0"]:
                if char =="1" or char =="0":
                    char="2"
                elif char == "7" or char =="8" or char == "9" or char=="10":
                    char="6"
                str += char
                lx.append(str)
                str = ""
            else:
                str += char
    if len(lx) > 1:
        note = lx
    for nt in note:
        try:
            if nt[1] != "#":
                num2 = int(nt[1]) * 12
                chr = nt[0]
            else:
                num2 = int(nt[2]) * 12
                chr = nt[0] + nt[1]
            chr = chr.replace("C#", "1").replace("D#", "3").replace("F#", "6").replace("G#", "8").replace("A#",
                                                                                                          "10").replace(
                "C", "0").replace("B", "11").replace("D", "2").replace("E", "4").replace("F", "5").replace("G",
                                                                                                           "7").replace(
                "A", "9")
            chr = int(chr)
            notenum.append(chr + num2)
        except:
            pass
    return notenum
def dsremove(list):
    if ".DS_Store" in list:
        list.remove(".DS_Store")
    return list

def trackstojson(trackfolder="tracks"):
    genres=dsremove(os.listdir(trackfolder))
    database={}
    for genre in genres:
        database[genre]={}
        songs=dsremove(os.listdir(trackfolder+"/"+genre))
        for song in songs:
            start=datetime.datetime.now()
            database[genre][song]={
                "path":trackfolder+"/"+genre+"/"+song,
                "midi":GenPlot.trackcombine(mido.MidiFile(trackfolder+"/"+genre+"/"+song, clip=True))
                }
            ins=[]
            i=0
            tracks, songname=database[genre][song]["midi"]
            for track in tracks:
                if track[1]=="insturment track":
                    ins.append([track[0],i])
                i+=1
            database[genre][song]["insturments"]={}
            for insturment in ins:
                #database[genre][song]["insturments"][insturment[0]]=miditosentences(database[genre][song]["path"])
                database[genre][song]["insturments"][insturment[0]] = {"index":insturment[1],"notes":tracktosentences(database[genre][song]["path"],insturment[1])}
                database[genre][song]["insturments"][insturment[0]]["pattern"]=trackPattern(database[genre][song]["insturments"][insturment[0]]["notes"])
            del database[genre][song]["midi"]
            print(song,str(datetime.datetime.now()-start))
    import json
    with open('data.txt', 'w') as outfile:
        json.dump(database, outfile,sort_keys=True)
    return database
def miditomodel(files):
    pass
def listtosentences(list,tempo):
        data = ""
        for note in list:
            duration = note[1]
            duration=str(round(10*(duration/tempo))/10)
            key=" ".join(note[0])
            data+="x".join(key.split(" "))+"w"+duration.replace(".","p").replace("/","s")+" "
        return data
def miditosentences2(trackname):
    file = md.converter.parse(trackname)
    partStream = file.parts.stream()
    notes = []
    for n in file.flat.notes:
        if "<music21.note." in str(n):
            note = str(n.pitch.name).replace("B-", "A#").replace("E-", "D#").replace("A-", "G#").replace("G-",
                                                                                                         "F#").replace(
                "D-", "C#")
            notes.append([note + "" + str(n.pitch.octave), n.quarterLength])
        if "<music21.chord.Chord" in str(n):
            chord = []
            for note in n.pitches:
                note = str(note).replace("B-", "A#").replace("E-", "D#").replace("A-", "G#").replace("G-",
                                                                                                     "F#").replace("D-",
                                                                                                                   "C#")

                note = note.replace("(<music21.pitch.Pitch ", "").replace(">,", "")
                chord.append(note)
            chord = str(chord).replace("[", "").replace("'", "").replace(",", "").replace("]", "")
            notes.append([chord, n.quarterLength])
    ctmp = 0
    data = ""
    for note in notes:
        duration = note[1]
        ctmp += duration
        if len(note[0]) > 3:
            note[0] = note[0].replace(" ", "")
        if duration >= 1.5:
            data += note[0] + ". "
            ctmp = 0
        else:
            if ctmp > 8:
                data += note[0] + ". "
                ctmp = 0
            else:
                data += note[0] + " "
    data += "."
    return data
def tracktosentences(file,index):
    midi=mido.MidiFile(file, clip=True)
    matrix=GenPlot.tracktoarray(GenPlot.trackcombine(midi)[0][index])
    notez=[]
    for _ in range(int(len(matrix)/127)):
        playing=librosa.midi_to_note(GenPlot.removenegative(matrix[_*127:(_+1)*127]))
        if notez != []:
            if notez[len(notez)-1][0]!=playing:
                    notez.append([playing,0])
            else:
                notez[len(notez)-1][1]+=1
        else:
            notez.append([playing,0])
    return listtosentences(notez,midi.ticks_per_beat)
def testsong(file):
    genre="test"
    song=file
    trackfolder="tracks"
    database={}
    database[genre]={}
    start = datetime.datetime.now()
    database[genre][file] = {
        "path": file,
        "midi": GenPlot.trackcombine(mido.MidiFile(song, clip=True))
    }
    ins = []
    i = 0
    tracks, songname = database[genre][song]["midi"]
    for track in tracks:
        if track[1] == "insturment track":
            ins.append([track[0], i])
        i += 1
    database[genre][song]["insturments"] = {}
    for insturment in ins:
        # database[genre][song]["insturments"][insturment[0]]=miditosentences(database[genre][song]["path"])
        database[genre][song]["insturments"][insturment[0]] = {"index": insturment[1],
                                                               "notes": tracktosentences(database[genre][song]["path"],
                                                                                         insturment[1])}
        database[genre][song]["insturments"][insturment[0]]["pattern"] = trackPattern(
            database[genre][song]["insturments"][insturment[0]]["notes"])
    del database[genre][song]["midi"]
    dict=database[genre][song]["insturments"]
    for insturment in dict:
        print(insturment,dict[insturment]["pattern"])