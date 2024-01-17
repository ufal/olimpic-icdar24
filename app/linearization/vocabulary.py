
NOTE_TYPE_TOKENS = [
    "1024th", "512th", "256th", "128th", "64th",
    "32nd", "16th", "eighth", "quarter", "half", "whole",
    "breve", "long", "maxima"
]

PITCH_TOKENS = [
    # ORDER MATTERS FOR COMPARISON!
    # (from lowest to highest pitch)
    "C0", "D0", "E0", "F0", "G0", "A0", "B0",
    "C1", "D1", "E1", "F1", "G1", "A1", "B1",
    "C2", "D2", "E2", "F2", "G2", "A2", "B2",
    "C3", "D3", "E3", "F3", "G3", "A3", "B3",
    "C4", "D4", "E4", "F4", "G4", "A4", "B4",
    "C5", "D5", "E5", "F5", "G5", "A5", "B5",
    "C6", "D6", "E6", "F6", "G6", "A6", "B6",
    "C7", "D7", "E7", "F7", "G7", "A7", "B7",
    "C8", "D8", "E8", "F8", "G8", "A8", "B8",
    "C9", "D9", "E9", "F9", "G9", "A9", "B9"
]

ALL_TOKENS = [
    "measure",
    *NOTE_TYPE_TOKENS,
    *PITCH_TOKENS,
    "rest",
    "rest:measure",
    "grace",
    "grace:slash",
    "chord",
]
