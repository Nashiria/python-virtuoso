import GenerateModel,os


def PatternAppend(trackfolder="tracks"):
    midilist = []
    for file in os.listdir(trackfolder):
        if ".mid" in file:
            midilist.append(trackfolder + "/" + file)
    allthetext = GenerateModel.sentencealltracks(midilist)
    allthetext = allthetext.replace(".", "")
    allthetext = allthetext.replace(" ", "-")
    allthetextList = allthetext.split("-")
    currentPattern = ""
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
        if len(x) > 10:
            if "" in x:
                x.remove("")
            final.append(x)
    v = []
    for pattern in final:
        patternnotes = list(dict.fromkeys(pattern))
        temp = []
        for note in pattern:
            temp.append(patternnotes.index(note))
        v.append(temp)
    return v
