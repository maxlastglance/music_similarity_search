from music21 import *


# Load the musicXML file into a Score object
#score = converter.parse('scores/PL-WRk_352_47r_Gaßenhauer_n22.musicxml')
#score = converter.parse('scores/A-Wn_Mus.Hs._18827_enc_dipl_CMN_1r-2r.mxl')
score = converter.parse('scores/PL-WRk_352_34r-35r_passo_n17.mxl')


melody_part  = score.parts[0].flat.notesAndRests.stream()
bass_part = score.parts[1].flat.notesAndRests.stream()

key = score.analyze('key')


root_notes = []

bass_previous = None

def getLowestNote(notes):
    lowest_note = None
    for bass_note in notes:
        if lowest_note is None or lowest_note.pitch.frequency > bass_note.pitch.frequency:
            lowest_note = bass_note

    return lowest_note

for note in bass_part.notes:
    if note.isChord:
        note = getLowestNote(note.notes)
    
    if bass_previous is None or (note.pitch != bass_previous.pitch):
        if len(bass_part.getElementsByOffset(note.offset)) > 1:
            notes_with_same_pitch = bass_part.getElementsByOffset(note.offset)
            lowest_note = getLowestNote(notes_with_same_pitch.notes)
            if bass_previous is None or (lowest_note.pitch != bass_previous.pitch):
                bass_previous = lowest_note
                root_notes.append(lowest_note)
        else:
            bass_previous = note
            root_notes.append(note)
        

for root in root_notes:
    print(roman.romanNumeralFromChord(chord.Chord([root]), key).figure)


