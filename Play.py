import fluidsynth
import time
from mido import MidiFile

sfz = "Piano.sf2"


def play(midi_file, speed, volume):
    fs = fluidsynth.Synth()
    fs.start(driver='portaudio')
    sfid = fs.sfload(sfz)
    fs.program_select(0, sfid, 0, 0)

    mid = MidiFile(midi_file, clip=True)
    for message in mid.tracks[0]:
        message = str(message).split(" ")
        status = message[0]
        if status == "note_on" or status == "note_off":
            channel = int(message[1].replace("channel=", ""))
            note = int(message[2].replace("note=", ""))
            velocity = int(message[3].replace("velocity=", ""))
            duration = int(message[4].replace("time=", ""))
            if velocity != 0:
                volume = round(velocity * volume)
                if volume > 127:
                    volume = 127
                fs.noteon(channel, note, (volume))
            else:
                fs.noteoff(channel, note)

            time.sleep((duration / 1000) / speed)
    fs.delete()
