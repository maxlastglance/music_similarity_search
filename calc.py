def calculate_values(true_positives, relevant_chords, retrieved_chords):
    """
    This method calculates precision, recall and f-measure rounded to
    one digit for given params and prints them out.

    :param true_positives: chords recognized correctly
    :param relevant_chords: overall number of relevant chords
    :param retrieved_chords: overall number of retrieved chords
    """
    precision = round((true_positives / retrieved_chords) * 100, 1)
    recall = round((true_positives / relevant_chords) * 100, 1)
    f_measure = round((2 * precision * recall) / (precision + recall), 1)

    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F-Measure: ", f_measure)


if __name__ == "__main__":
    print("Overall rule-based: ")
    calculate_values(19, 19, 69)
    print("Overall rule-based optimized: ")
    calculate_values(11, 19, 34)
    print("Overall crf: ")
    calculate_values(19, 19, 26)
