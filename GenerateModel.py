import music21 as md
import os
import random
import gensim,librosa
def PatternAppend(midilist):
    v = []
    for midi in midilist:
        print(midi)
        allthetext = miditosentences(midi)
        allthetext=allthetext.replace(".","")
        allthetext=allthetext.replace(" ","-")
        allthetextList=allthetext.split("-")
        currentPattern=""
        allpatterns=[]
        for note in allthetextList:
            currentPattern+=note+"-"
            if allthetext.count(currentPattern)>2:
                pass
            else:
                allpatterns.append(currentPattern)
                currentPattern=""
        mylist = list(dict.fromkeys(allpatterns))
        final=[]
        for pat in mylist:
            x=pat.split("-")
            if len(x)>10:
                if "" in x:
                    x.remove("")
                final.append(x)

        for pattern in final:
            patternnotes=list(dict.fromkeys(pattern))
            temp=[]
            for note in pattern:
                temp.append(patternnotes.index(note))
            v.append(temp)
    return v

def miditosentences(trackname):
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
def evaluatedata(alldata):
    sentences = alldata.split(".")
    nwlist = []
    for sentence in sentences:
        v = str(sentence)
        v = v.split(" ")
        sentence = v
        if "" in sentence:
            sentence.remove("")
        nwlist.append(sentence)
    sentences = nwlist
    model = gensim.models.Word2Vec(sentences, size=500)
    model.train(sentences, total_examples=len(sentences), epochs=100)
    model.init_sims(replace=True)
    model.save("midimodel.model")
    return model
def sentencealltracks(tracklist):
    data = ""
    if len(tracklist)!=0:
        for trackname in tracklist:
            print(trackname)
            text = miditosentences(trackname)
            data += text
    return data
def notetomidivalue(note):
    notenum = []
    str = ""
    lx = []
    if len(note) < 4:
        note = [note]
    else:
        for char in note:
            if char in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0"]:
                str += char
                lx.append(str)
                str = ""
            else:
                str += char
    if len(lx) > 1:
        note = lx
    for nt in note:
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
    return notenum
def notetomidivalue2(note):
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

def modelgenerate(filename, trackfolder):
    filenamepath = "./" + filename + ".model"
    filename = filename + ".model"
    if (os.path.isfile(filename)):  # if there is a model saved, load it
        model = gensim.models.Word2Vec.load(filename)
    else:
        midilist = []
        for file in os.listdir(trackfolder):
            if ".mid" in file:
                midilist.append(trackfolder+"/"+file)
        patterns=PatternAppend(midilist)
        out={}
        out["patterns"]=patterns
        import json
        with open('patterns.json', 'w') as outfile:
            json.dump(out, outfile)
        print("done")
        allthetext = sentencealltracks(midilist)
        model = evaluatedata(allthetext)
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
