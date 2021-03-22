import string

import librosa
import matplotlib.pyplot as plt
import mido
import numpy as np


def trackcombine(mid):
    alltracks=[]

    songname="No name"
    for track in mid.tracks:
        trackmessages=[]
        trackname = "Untitled Track"
        insturment="Untitled"
        notes=False
        for message in track:
            if "track_name name" in str(message):
                trackname=str(message).split("'")
                trackname=trackname[1]
            if "message text text" in str(message):
                trackname=str(message).split("'")
                insturment=trackname[1]
            if "note_on" in str(message):
                notes=True
            if "message marker text" in str(message):
                songname = str(message).split("'")
                songname = songname[1]
            trackmessages.append(str(message))
        if notes:
            notes="insturment track"
        else:
            notes="metadata track"
        if "Untitled" not in trackname:
            if "Untitled" not in insturment:
                trackname=insturment
        alltracks.append([trackname,notes,trackmessages])
    return alltracks,songname.replace("  "," ").replace("  "," ")
def playingmatrix(playingnotes):
    empty=[0]*127
    for note in playingnotes:
        empty[note]=note
    return empty
def tracktoarray(track):
    messages=track[2]
    notesplaying={}
    array=[]
    totaltime=0
    for message in messages:
        if "note_" in message:
            message=message.split(" ")
            status=message[0]
            channel = int(message[1].replace("channel=", ""))
            note = (int(message[2].replace("note=", "")))
            velocity = int(message[3].replace("velocity=", ""))
            time = int(message[4].replace("time=", ""))
            totaltime+=time
            if status=="note_off":
                velocity=0
            if velocity!=0:
                notesplaying[note]={"time":time}
            if velocity==0:
                notesonline=[]
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

def showplot(array,filename,timeinseconds):
    times = []
    seconds = 0
    if len(array)==1:
        fig, axs = plt.subplots(len(array))
    else:
        fig, axs = plt.subplots(len(array),figsize=(3*len(array),4*len(array)))
    for _ in range(len(array)):
            arr=array[_]
            trar=tracktoarray(arr)
            ar=removenegative(trar)
            ticks=0
            if len(array) == 1:
                axs.set_title(filename.replace("GeneratedPlots/","").replace(".mid","").replace(".png","")+" - "+arr[0]+"\n"+"Duration: "+str(timeinseconds)+" seconds")
                axs.plot(range(len(ar)),ar, marker='.', markersize=1, linestyle='')
                axs.tick_params(axis='x',which='both', bottom=False, top=False, labelbottom=False)
                axs.set_ylabel('Note')
            else:
                if _==0:
                    axs[_].set_title("Duration: "+str(timeinseconds)+" seconds"+"\n"+filename.replace("GeneratedPlots/", "").replace(".mid", "").replace(".png","")+ " - " + arr[0])
                else:
                    axs[_].set_title(filename.replace("GeneratedPlots/", "").replace(".mid", "").replace(".png","")+ " - " + arr[0])

                axs[_].plot(range(len(ar)),ar, marker='.', markersize=1, linestyle='')
                #plt.xticks(rotation=90)
                axs[_].tick_params(axis='x',which='both', bottom=False, top=False, labelbottom=False)
                axs[_].set_ylabel('Note')
    if "GeneratedPlots/" not in filename:
            filename="GeneratedPlots/"+filename.replace(" .mid","")+".png"
    filename=filename.replace(" .png",".png")
    if "Generated/" in filename:
        filename=filename.replace("Generated/","")
    plt.savefig(filename)
    plt.tight_layout()
    plt.show()
    return array
def showplotofmidi(midi_file, filename):
    mid = mido.MidiFile(midi_file, clip=True)
    alltracks,songname=trackcombine(mid)
    instracks=[]
    for track in alltracks:
       if len(track)>2:
           if track[1]=="insturment track":
               instracks.append(track)
    if songname=="No name":
        showplot(instracks,filename,round(mid.length))
    else:
        showplot(instracks, songname,round(mid.length))
