# Chord Recognition In Medieval Lute Tablatures

This repository represents the practical part of my bachelor thesis "Chord Recognition In Medieval Lute Tablatures". It is the implementation of a simple rule based approach to recognize chords
in medieval lute tablatures. In the paper it is compared to a state of the art chord recognition tool using conditional random fields.

In the scores folder you can find the .mxl files of the two running example from the paper and the output file of the CRF approach. 

## Run the code

To run the code after installing the required packages you can use the following command line commands:

```
$ python3 extract_chords_bass.py <file_path> --optimized <True/False>
```

To evaluate a .txt file in the format of the CRF output just run:

```
$ python3 extract_chords_bass.py <file_path>
```

Note that scores for the rule-based approach must have .mxl or .musicxml file extension and CRF output files .txt extension.
