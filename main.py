from music21 import *


# Load the musicXML file into a Score object
score = converter.parse('scores/PL-WRk_352_47r_Gaßenhauer_n22.musicxml')

def chordsAreEqual(chordOne, chordTwo):
    if chordOne.pitches == chordTwo.pitches:
        return True
    
    pitchNamesOne = []
    pitchNamesTwo = []
    
    for pitch in chordOne.pitches:
        if pitch.unicodeName not in pitchNamesOne:
            pitchNamesOne.append(pitch.unicodeName)

    for pitch in chordTwo.pitches:
        if pitch.unicodeName not in pitchNamesTwo:
            pitchNamesTwo.append(pitch.unicodeName)
    
    return set(pitchNamesOne) == set(pitchNamesTwo)



print("CHORDS: ", len(score.chordify().recurse().getElementsByClass('Chord')))

chords = score.chordify().recurse().getElementsByClass('Chord')
filteredChords = []
previousChord = chord.Chord([])


for chord in chords:
    if (chord.isMajorTriad() or chord.isMinorTriad()) and (not chordsAreEqual(chord, previousChord)):
        filteredChords.append(chord)
        previousChord = chord


for chord in filteredChords:
    print(chord.root(), "Dur" if chord.isMajorTriad() else "Moll")




