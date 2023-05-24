from music21 import *


# Load the musicXML file into a Score object
#score = converter.parse('scores/PL-WRk_352_47r_Gaßenhauer_n22.musicxml')
#score = converter.parse('scores/A-Wn_Mus.Hs._18827_enc_dipl_CMN_1r-2r.mxl')
score = converter.parse('scores/PL-WRk_352_34r-35r_passo_n17.musicxml')

melody_part  = score.parts[0].flat.notesAndRests.stream()
bass_part = score.parts[1].flat.notesAndRests.stream()


timeSignature = score.getTimeSignatures()[0]

key = score.analyze('key')


root_notes = []

bass_previous = None

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

for note in bass_part.notes:
    if note.isChord:
        note = getLowestNote(note.notes)

        #only note with different pitch than previous note are taken into account    
    if bass_previous is None or (note.pitch != bass_previous.pitch):
        #if there is more than one note at the same time, we get the lowest
        if len(bass_part.getElementsByOffset(note.offset)) > 1:
            notes_with_same_pitch = bass_part.getElementsByOffset(note.offset)
            lowest_note = getLowestNote(notes_with_same_pitch.notes)
            #if first note or pitch is different -> note is appended
            root_notes = checkAndAppendTwo(bass_previous, lowest_note, root_notes, timeSignature)
            bass_previous = root_notes[-1]            
        else:
            root_notes = checkAndAppendTwo(bass_previous, note, root_notes, timeSignature)
            bass_previous = root_notes[-1]
        
        

for root in root_notes:
    print(roman.romanNumeralFromChord(chord.Chord([root]), key).figure, root.offset)


