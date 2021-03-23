import matplotlib.pyplot as plt
import mido

def findinsturment(program):
    Insturments={0:'Acoustic Grand Piano',
                1:'Bright Acoustic Piano',
                2:'Electric Grand Piano',
                3:'Honky-tonk Piano',
                4:'Electric Piano 1',
                5:'Electric Piano 2',
                6:'Harpsichord',
                7:'Clavinet',
                8:'Celesta',
                9:'Glockenspiel',
                10:'Music Box',
                11:'Vibraphone',
                12:'Marimba',
                13:'Xylophone',
                14:'Tubular Bells',
                15:'Dulcimer',
                16:'Drawbar Organ',
                17:'Percussive Organ',
                18:'Rock Organ',
                19:'Church Organ',
                20:'Reed Organ',
                21:'Accordion',
                22:'Harmonica',
                24:'Acoustic Guitar (nylon)',
                25:'Acoustic Guitar (steel)',
                26:'Electric Guitar (jazz)',
                27:'Electric Guitar (clean)',
                28:'Electric Guitar (muted)',
                29:'Overdriven Guitar',
                30:'Distortion Guitar',
                31:'Guitar Harmonics',
                32:'Acoustic Bass',
                33:'Electric Bass (finger)',
                34:'Electric Bass (pick)',
                35:'Fretless Bass',
                36:'Slap Bass 1',
                37:'Slap Bass 2',
                38:'Synth Bass 1',
                39:'Synth Bass 2',
                40:'Violin',
                41:'Viola',
                42:'Cello',
                43:'Contrabass',
                44:'Tremolo Strings',
                45:'Pizzicato Strings',
                46:'Orchestral Harp',
                47:'Timpani',
                48:'String Ensemble 1',
                49:'String Ensemble 2',
                50:'Synth Strings 1',
                51:'Synth Strings 2',
                52:'Choir Aahs',
                53:'Voice Oohs',
                54:'Synth Choir',
                55:'Orchestra Hit',
                56:'Trumpet',
                57:'Trombone',
                58:'Tuba',
                59:'Muted Trumpet',
                60:'French Horn',
                61:'Brass Section',
                62:'Synth Brass 1',
                63:'Synth Brass 2',
                64:'Soprano Sax',
                65:'Alto Sax',
                66:'Tenor Sax',
                67:'Baritone Sax',
                68:'Oboe',
                69:'English Horn',
                70:'Bassoon',
                71:'Clarinet',
                72:'Piccolo',
                73:'Flute',
                74:'Recorder',
                75:'Pan Flute',
                76:'Blown bottle',
                77:'Shakuhachi',
                78:'Whistle',
                79:'Ocarina',
                80:'Lead 1 (square)',
                81:'Lead 2 (sawtooth)',
                82:'Lead 3 (calliope)',
                83:'Lead 4 (chiff)',
                84:'Lead 5 (charang)',
                85:'Lead 6 (voice)',
                86:'Lead 7 (fifths)',
                87:'Lead 8 (bass + lead)',
                88:'Pad 1 (new age)',
                89:'Pad 2 (warm)',
                90:'Pad 3 (polysynth)',
                91:'Pad 4 (choir)',
                92:'Pad 5 (bowed)',
                93:'Pad 6 (metallic)',
                94:'Pad 7 (halo)',
                95:'Pad 8 (sweep)',
                96:'FX 1 (rain)',
                97:'FX 2 (soundtrack)',
                98:'FX 3 (crystal)',
                99:'FX 4 (atmosphere)',
                100:'FX 5 (brightness)',
                101:'FX 6 (goblins)',
                102:'FX 7 (echoes)',
                103:'FX 8 (sci-fi)',
                104:'Sitar',
                105:'Banjo',
                106:'Shamisen',
                107:'Koto',
                108:'Kalimba',
                109:'Bagpipe',
                110:'Fiddle',
                111:'Shanai',
                112:'Tinkle Bell',
                113:'Agogo',
                114:'Steel Drums',
                115:'Woodblock',
                116:'Taiko Drum',
                117:'Melodic Tom',
                118:'Synth Drum',
                119:'Reverse Cymbal',
                120:'Guitar Fret Noise',
                121:'Breath Noise',
                122:'Seashore',
                123:'Bird Tweet',
                124:'Telephone Ring',
                125:'Helicopter',
                126:'Applause',
                127:'Gunshot',
                128:'Unknown'}
    return Insturments[program]

def trackcombine(mid):
    alltracks = []
    songname = "No name"
    for track in mid.tracks:
        trackmessages = []
        trackname = "Untitled Track"
        insturment = []
        notes = False
        for message in track:
            if "track_name name" in str(message):
                trackname = str(message).split("'")
                trackname = trackname[1]
            if "note_on" in str(message):
                notes = True
            if "message marker text" in str(message):
                songname = str(message).split("'")
                songname = songname[1]
            if "program_change" in str(message):
                ls = str(message).split(" ")
                insturment.append(int(ls[2].replace("program=", "")))
            trackmessages.append(str(message))
        if notes:
            notes = "insturment track"
            if "drum" in trackname.lower():
                trackname = "Drums"
            else:
                if len(insturment)<1:
                    insturment.append(128)
                insturment = findinsturment(max(set(insturment), key=insturment.count))
                trackname = insturment
        else:
            notes = "metadata track"
        alltracks.append([trackname, notes, trackmessages])
    return alltracks, songname.replace("  ", " ").replace("  ", " ")


def playingmatrix(playingnotes):
    empty = [0] * 127
    for note in playingnotes:
        empty[note] = note
    return empty


def tracktoarray(track):
    messages = track[2]
    notesplaying = {}
    array = []
    totaltime = 0
    for message in messages:
        if "note_" in message:
            message = message.split(" ")
            status = message[0]
            channel = int(message[1].replace("channel=", ""))
            note = (int(message[2].replace("note=", "")))
            velocity = int(message[3].replace("velocity=", ""))
            time = int(message[4].replace("time=", ""))
            totaltime += time
            if status == "note_off":
                velocity = 0
            if velocity != 0:
                notesplaying[note] = {"time": time}
            if velocity == 0:
                notesonline = []
                for notec in notesplaying:
                    notesonline.append(notec)
                notesonline.sort()
                array.extend(playingmatrix(notesonline) * time)
                try:
                    del notesplaying[note]
                except:
                    pass
    return array


def removenegative(array):
    return list(filter((0).__ne__, array))


def showplot(array, filename, timeinseconds):
    times = []
    seconds = 0
    if len(array) == 1:
        fig, axs = plt.subplots(len(array))
    else:
        fig, axs = plt.subplots(len(array), figsize=(3 * len(array), 4 * len(array)))
    for _ in range(len(array)):
        arr = array[_]
        trar = tracktoarray(arr)
        ar = removenegative(trar)
        ticks = 0
        if len(array) == 1:
            axs.set_title(filename.replace("GeneratedPlots/", "").replace(".mid", "").replace(".png", "") + " - " + arr[
                0] + "\n" + "Duration: " + str(timeinseconds) + " seconds")
            axs.plot(range(len(ar)), ar, marker='.', markersize=1, linestyle='')
            axs.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            axs.set_ylabel('Note')
        else:
            if _ == 0:
                axs[_].set_title(
                    "Duration: " + str(timeinseconds) + " seconds" + "\n" + filename.replace("GeneratedPlots/",
                                                                                             "").replace(".mid",
                                                                                                         "").replace(
                        ".png", "") + " - " + arr[0])
            else:
                axs[_].set_title(
                    filename.replace("GeneratedPlots/", "").replace(".mid", "").replace(".png", "") + " - " + arr[0])

            axs[_].plot(range(len(ar)), ar, marker='.', markersize=1, linestyle='')
            # plt.xticks(rotation=90)
            axs[_].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            axs[_].set_ylabel('Note')
    if "GeneratedPlots/" not in filename:
        filename = "GeneratedPlots/" + filename.replace(" .mid", "") + ".png"
    filename = filename.replace(" .png", ".png")
    if "Generated/" in filename:
        filename = filename.replace("Generated/", "")
    plt.savefig(filename)
    plt.tight_layout()
    plt.show()
    return array


def showplotofmidi(midi_file, filename):
    mid = mido.MidiFile(midi_file, clip=True)
    alltracks, songname = trackcombine(mid)
    instracks = []
    for track in alltracks:
        if len(track) > 2:
            if track[1] == "insturment track":
                instracks.append(track)
    if songname == "No name":
        showplot(instracks, filename, round(mid.length))
    else:
        showplot(instracks, songname, round(mid.length))
