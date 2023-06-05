from music21 import *



def getTimingModulo(timing):
    numerator = timing.beatCount
    denominator = int(timing.barDuration.quarterLength)

    if numerator == 4 and denominator == 4:
        return 2
    else:
        return denominator


#only checks if the note changed
def checkAndAppend(previousNote, note, noteList, timing):
    if previousNote is None or (note.pitch != previousNote.pitch):
            previousNote = note
            noteList.append(note)
    return noteList


#furthermore checks if there are small notes and ignores them
#additionally, only heavy counts are recognized
def checkAndAppendTwo(previousNote, note, noteList, timing):

    timing_modulo = getTimingModulo(timing)
    if previousNote is None or (note.pitch != previousNote.pitch):
        if note.offset % timing_modulo > 0:
            return noteList        
        if note.duration.type == "16th":
            return noteList
        if note.duration.type == "eigth" and previousNote.duration.type == "eigth":
            return noteList
        
        noteList.append(note)

    return noteList

def getLowestNote(notes):
    lowest_note = None
    for bass_note in notes:
        if lowest_note is None or lowest_note.pitch.frequency > bass_note.pitch.frequency:
            lowest_note = bass_note

    return lowest_note

def getRomanNumerals(root_notes):
    numerals = []
    for root in root_notes:
        #numerals.append(roman.romanNumeralFromChord(chord.Chord([root]), key))
        print(roman.romanNumeralFromChord(chord.Chord([root]), key).figure, root.offset)

def checkForVariationOne(numerals):
    #check if I-VII-I-V occurs in the score (and how often)
    counter = 0

    for i in range(len(numerals)):
        if(numerals[i] == "i" and i + 3 < len(numerals) and numerals[i + 1] == "bvii" and numerals[i + 2] == "i" and
        numerals[i + 3] == "v"):
            counter += 1
            i += 4

    return counter

def checkForVariationTwo(numerals):
    #check if there is the formula with other chords instead of the I degree in between
    counter = 0
    comments = []

    for i in range(len(numerals)):
        if (i + 1 < len(numerals) and numerals[i] == "i" and numerals[i + 1] == "bvii"):
            for j in range(2, 6):
                if i + j < len(numerals) and numerals[i + j] == "v":
                    counter += 1
                    comments.append("there are " + str(j-2) + " chords between VII and V")
                    i = i + j
                    break
    return [counter, comments]

def checkForVariationThree(numerals):
    counter = 0
    comments = []

    for i in range(len(numerals)):
        if (numerals[i] == "i"):
            for j in range(2, 6):
                comment = ""
                #first search for seventh degree
                if i + j < len(numerals) and  numerals[i + j] == "bvii":
                    #since we found seventh degree, now let's look for fifth degree
                    comment += "there are " + str(j - 1) + " chords between I and VII"
                    for p in range(1, 6):
                        k = i + j + p
                        if k < len(numerals) and numerals[k] == "v":
                            comment += " and " + str(p - 1) + " chords between VII and V"
                            comments.append(comment)
                            counter += 1
                            i = k
                            break
            break


    return [counter, comments]

def checkForVariationFour(numerals):
    #check if I-V-I-VII occurs in the score (and how often)
    counter = 0

    for i in range(len(numerals)):
        if(numerals[i] == "i" and i + 3 < len(numerals) and numerals[i + 1] == "v" and numerals[i + 2] == "i" and
        numerals[i + 3] == "bvii"):
            counter += 1
            i += 4

    return counter

def checkForSevenOnOne(numerals):
    counter = 0
    for i in range(len(numerals) - 1):
        if numerals[i] == "i" and numerals[i + 1] == "bvii":
            counter += 1
    return counter

def checkForSevenOnOneWithNoise(numerals):
    #check if there is the formula with other chords instead of the I degree in between
    counter = 0
    comments = []

    for i in range(len(numerals)):
        if (i + 1 < len(numerals) and numerals[i] == "i"):
            for j in range(2, 6):
                if i + j < len(numerals) and numerals[i + j] == "bvii":
                    counter += 1
                    comments.append("there are " + str(j-1) + " chords between I and VII")
                    break
    return [counter, comments]

def main():
    # Load the musicXML file into a Score object
    # score = converter.parse('scores/PL-WRk_352_47r_Gaßenhauer_n22.musicxml')
    # score = converter.parse('scores/A-Wn_Mus.Hs._18827_enc_dipl_CMN_1r-2r.mxl')
    score = converter.parse('scores/PL-WRk_352_34r-35r_passo_n17.musicxml')

    melody_part = score.parts[0].flat.notesAndRests.stream()
    bass_part = score.parts[1].flat.notesAndRests.stream()

    timeSignature = score.getTimeSignatures()[0]

    key = score.analyze('key')

    root_notes = []

    bass_previous = None

    for note in bass_part.notes:
        if note.isChord:
            note = getLowestNote(note.notes)

            # only note with different pitch than previous note are taken into account
        if bass_previous is None or (note.pitch != bass_previous.pitch):
            # if there is more than one note at the same time, we get the lowest
            if len(bass_part.getElementsByOffset(note.offset)) > 1:
                notes_with_same_pitch = bass_part.getElementsByOffset(note.offset)
                lowest_note = getLowestNote(notes_with_same_pitch.notes)
                # if first note or pitch is different -> note is appended
                root_notes = checkAndAppend(bass_previous, lowest_note, root_notes, timeSignature)
                bass_previous = root_notes[-1]
            else:
                root_notes = checkAndAppend(bass_previous, note, root_notes, timeSignature)
                bass_previous = root_notes[-1]

    numerals = []
    for root in root_notes:
        numerals.append(roman.romanNumeralFromChord(chord.Chord([root]), key).figure)

    print("found basic formula (I-VII-I-V) " + str(checkForVariationOne(numerals)) + " times")
    result = checkForVariationTwo(numerals)

    print(f"found variation two (I-VII-...-V) {result[0]} times")
    for comment in result[1]:
        print(comment)

    result = checkForVariationThree(numerals)
    print(f"found variation three (I-...-VII-...-V) {result[0]} times")
    for comment in result[1]:
        print(comment)

    print("found variation four (I-V-I-VII) " + str(checkForVariationFour(numerals)) + " times")
    print("I is followed by VII " + str(checkForSevenOnOne(numerals)) + " times")

    result = checkForSevenOnOneWithNoise(numerals)

    print("found variation five (I-...-VII) " + str(result[0]) + " times")
    for comment in result[1]:
        print(comment)


    for obj in numerals:
        print(obj)




main()





