KEY_TOKENS = [
    "key:fifths:-7", "key:fifths:-6", "key:fifths:-5", "key:fifths:-4",
    "key:fifths:-3", "key:fifths:-2", "key:fifths:-1",
    "key:fifths:0",
    "key:fifths:1", "key:fifths:2", "key:fifths:3", "key:fifths:4",
    "key:fifths:5", "key:fifths:6", "key:fifths:7",
]

BEATS_TOKENS = [
    "beats:1", "beats:2", "beats:3", "beats:4", "beats:5", "beats:6",
    "beats:7", "beats:8", "beats:9", "beats:10", "beats:11", "beats:12",
    "beats:13", "beats:14", "beats:15", "beats:16"
]

BEAT_TYPE_TOKENS = [
    "beat-type:2",
    "beat-type:4",
    "beat-type:8",
    "beat-type:16"
]

TIME_SIGNATURE_TOKENS = [
    "time",
    *BEATS_TOKENS,
    *BEAT_TYPE_TOKENS
]

CLEF_TOKENS = [
    "clef:G1", "clef:G2", "clef:G3", "clef:G4", "clef:G5",
    "clef:C1", "clef:C2", "clef:C3", "clef:C4", "clef:C5",
    "clef:F1", "clef:F2", "clef:F3", "clef:F4", "clef:F5"
]

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
    *KEY_TOKENS,
    *TIME_SIGNATURE_TOKENS,
    *CLEF_TOKENS,
    # "backup",
    # "forward",
    *NOTE_TYPE_TOKENS,
    *PITCH_TOKENS,
    "rest",
    "rest:measure",
    "grace",
    "grace:slash",
    "chord",
]
