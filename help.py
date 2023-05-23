from music21 import *


# Load the musicXML file into a Score object
#score = converter.parse('scores/PL-WRk_352_47r_Gaßenhauer_n22.musicxml')
score = converter.parse('scores/A-Wn_Mus.Hs._18827_enc_dipl_CMN_1r-2r.mxl')

score.parts[1].show()