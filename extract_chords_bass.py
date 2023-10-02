import music21
from music21 import key, note, roman, chord, converter
import sys
import argparse
import time


def get_timing_modulo(timing):
    """
    Check if the bars are even or odd.

    :param timing: timing associated with the song
    :return: 2 if it is an even metric with four beats,
            the denominator else
    """
    numerator = timing.beatCount
    denominator = int(timing.barDuration.quarterLength)

    if numerator == 4 and denominator == 4:
        return 2
    else:
        return denominator


def check_and_append(previous_note, note, note_list):
    """
    Appending notes to the list without any optimizations.

    :param previous_note: note played before
    :param note: note to evaluate
    :param note_list: list of all notes added already
    :return: current list of notes
    """
    if previous_note is None or (note.pitch != previous_note.pitch):
        note_list.append(note)
    return note_list


def check_and_append_two(previous_note, note, note_list, timing):
    """
    Similar to checkAndAppend but does some optimizations in timing.

    :param previous_note: note played before
    :param note: note to evaluate
    :param note_list: list of all notes added already
    :param timing of the song to only add notes on heavy beats
    :return: current list of notes
    """

    timing_modulo = get_timing_modulo(timing)
    if previous_note is None or (note.pitch != previous_note.pitch):
        if note.offset % timing_modulo > 0:
            return note_list
        if note.duration.type == "16th":
            return note_list
        if note.duration.type == "eigth" and \
                previous_note.duration.type == "eigth":
            return note_list

        note_list.append(note)

    return note_list


def get_lowest_note(notes):
    """
    Finds the lowest note in provided list.
    :param notes: list of candidates
    :return: lowest note in the given list
    """
    lowest_note = None
    for bass_note in notes:
        if not bass_note.isChord and (lowest_note is None or
                                      lowest_note.pitch.frequency > bass_note.pitch.frequency):
            lowest_note = bass_note

        if bass_note.isChord:
            lowest_note = note.Note(bass_note.root())

    return lowest_note


def print_roman_numerals(root_notes):
    """
    Prints out the roman numeral representation of note.

    :param root_notes: root notes of the song
    """
    for root in root_notes:
        print(roman.romanNumeralFromChord(chord.Chord([root]),
                                          key).figure, root.offset)


def check_for_variation_one(numerals):
    """
    Checks if I-VII-I-V is present in the numerals.

    :param numerals: Roman numerals of song
    :return: number of occurrences of the form
    """
    counter = 0

    for i in range(len(numerals)):
        if (numerals[i] == "i" and i + 3 < len(numerals) and
                numerals[i + 1] == "bvii" and numerals[i + 2] == "i" and
                numerals[i + 3] == "v"):
            counter += 1
            i += 4

    return counter


def check_for_variation_two(numerals):
    """
    Checks if I-VII-I-V is present in the numerals, but accepts notes in
    between.

    :param numerals: Roman numerals of song
    :return: number of occurrences of the form and comments on
        how many notes are in between
    """
    counter = 0
    comments = []

    for i in range(len(numerals)):
        if (i + 1 < len(numerals) and
                numerals[i] == "i" and numerals[i + 1] == "bvii"):
            for j in range(2, 6):
                if i + j < len(numerals) and numerals[i + j] == "v":
                    counter += 1
                    comments.append("there are " + str(j - 2) +
                                    " chords between VII and V")
                    i = i + j
                    break
    return [counter, comments]


def check_for_variation_three(numerals):
    """
    Checks if I-...-VII-...-V is present in the numerals.

    :param numerals: Roman numerals of song
    :return: number of occurrences of the form and comments on
        how many notes are in between
    """
    counter = 0
    comments = []

    for i in range(len(numerals)):
        if (numerals[i] == "i"):
            for j in range(2, 6):
                comment = ""
                if i + j < len(numerals) and \
                        numerals[i + j] == "bvii":
                    comment += "there are " + str(j - 1) + \
                               " chords between I and VII"
                    for p in range(1, 6):
                        k = i + j + p
                        if k < len(numerals) and numerals[k] == "v":
                            comment += " and " + str(p - 1) + \
                                       " chords between VII and V"
                            comments.append(comment)
                            counter += 1
                            i = k
                            break
            break

    return [counter, comments]


def check_for_variation_four(numerals):
    """
    Checks if I-V-I-VII is present in the code.

    :param numerals: Roman numerals of song
    :return: number of occurrences of the form and comments on
        how many notes are in between
    """
    counter = 0

    for i in range(len(numerals)):
        if (numerals[i] == "i" and i + 3 < len(numerals) and
                numerals[i + 1] == "v" and numerals[i + 2] == "i" and
                numerals[i + 3] == "bvii"):
            counter += 1
            i += 4

    return counter


def check_for_seven_on_one(numerals):
    """
    Checks how often VII is followed by I.

    :param numerals: Roman numerals of song
    :return: number of occurrences of the form and comments on
        how many notes are in between
    """
    counter = 0
    for i in range(len(numerals) - 1):
        if numerals[i] == "i" and numerals[i + 1] == "bvii":
            counter += 1
    return counter


def check_for_seven_on_one_with_noise(numerals):
    """
    Checks how often VII is followed by I, but accepts
    other chords in between.

    :param numerals: Roman numerals of song
    :return: number of occurrences of the form and comments on
        how many notes are in between
    """
    counter = 0
    comments = []

    for i in range(len(numerals)):
        if (i + 1 < len(numerals) and numerals[i] == "i"):
            for j in range(2, 6):
                if i + j < len(numerals) and \
                        numerals[i + j] == "bvii":
                    counter += 1
                    comments.append("there are " + str(j - 1) + " chords between I and VII")
                    break
    return [counter, comments]


def extract_roots(bass_part, time_signature, optimized=False):
    """
    Extracts the root notes of the chords. Uses other methods to do so.

    :param bass_part: all bass notes of the song
    :param time_signature: timing denominator
    :param optimized: indicates which append method is used
    :return: root notes of the chords
    """
    bass_previous = None
    root_notes = []

    for tmp_note in bass_part.notes:
        if tmp_note.isChord:
            tmp_note = get_lowest_note(tmp_note.notes)

        if bass_previous is None or \
                (tmp_note.pitch != bass_previous.pitch):
            # if there is more than one note at the same time, we get the lowest
            if len(bass_part.getElementsByOffset(tmp_note.offset)) > 1:
                notes_with_same_pitch = bass_part.getElementsByOffset(tmp_note.offset)
                lowest_note = get_lowest_note(notes_with_same_pitch.notes)
                # if first note or pitch is different -> note is appended
                if optimized:
                    root_notes = check_and_append_two(bass_previous,
                                                      lowest_note, root_notes, time_signature)
                else:
                    root_notes = check_and_append(bass_previous,
                                                  lowest_note, root_notes)
                bass_previous = root_notes[-1]
            else:
                if optimized:
                    root_notes = check_and_append_two(bass_previous,
                                                      tmp_note,
                                                      root_notes,
                                                      time_signature)
                else:
                    root_notes = check_and_append(bass_previous,
                                                  tmp_note,
                                                  root_notes)
                bass_previous = root_notes[-1]

    return root_notes


def extract_numerals(root_notes, key):
    """
    Gets roman numerals representation from provided root notes.

    :param root_notes: root notes of song
    :param key: key of the song
    :return: roman numeral representation of root_notes
    """
    numerals = []
    prevNote = music21.note.Note()
    for root in root_notes:
        if prevNote.name is not root.name:
            numerals.append(roman.romanNumeralFromChord(chord.Chord([root]), key).figure)
            prevNote = root

    return numerals


def print_result_from_numerals(numerals):
    """
    Prints which passa mezo forms where found and all found chords.

    :param numerals: chords of song in roman numeral representation.
    :return:
    """
    print("found basic formula (I-VII-I-V) " + str(check_for_variation_one(numerals)) + " times")
    result = check_for_variation_two(numerals)

    print(f"found variation two (I-VII-...-V) {result[0]} times")
    for comment in result[1]:
        print(comment)

    result = check_for_variation_three(numerals)
    print(f"found variation three (I-...-VII-...-V) {result[0]} times")
    for comment in result[1]:
        print(comment)

    print("found variation four (I-V-I-VII) " + str(check_for_variation_four(numerals)) + " times")
    print("I is followed by VII " + str(check_for_seven_on_one(numerals)) + " times")

    print("Found chords: ")
    for i, obj in enumerate(numerals):
        print(obj, end=", ")
        if (i + 1) % 20 == 0:
            print()

    print("Overall number of recognized chords: ", len(numerals))


def extract_roots_from_crf():
    """
    Helper method to extract roots from external semi-CRF approach.

    :return: root notes of given semi-CRF output file
    """
    filename = sys.argv[1]
    root_notes = []

    with open(filename, 'r') as file:
        for line in file:
            tmp = line.strip().split(' ')
            if tmp[0] == 'Actual:':
                predicted = tmp[5]

                if not root_notes or note.Note(predicted[0]) != root_notes[-1]:
                    root_notes.append(note.Note(predicted[0]))

    return root_notes


def str2bool(v):
    """
    Checks different boolean representations of string. Helper
    method for command line interface.

    :param v: given variable
    :return: true or false depending on v
    """
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    """
    Main method, calls all the other methods and runs the approach
    according to command line interface. Results are printed out
    via several methods.
    """
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to file')
    parser.add_argument('--optimized', type=str2bool, help='Boolean flag')
    args = parser.parse_args()
    score_path = args.path

    if score_path.endswith(".mxl") or score_path.endswith(".musicxml"):
        score = converter.parse(score_path)

        bass_part = score.parts[1].flat.notesAndRests.stream()
        time_signature = score.getTimeSignatures()[0]
        tonic = score.analyze('key')
        root_notes = extract_roots(bass_part, time_signature, args.optimized)
    else:
        root_notes = extract_roots_from_crf()
        tonic = key.Key(root_notes[0].name)
    numerals = extract_numerals(root_notes, tonic)

    print_result_from_numerals(numerals)
    end = time.time()
    print("Time elapsed: ", end - start)


if __name__ == "__main__":
    main()
