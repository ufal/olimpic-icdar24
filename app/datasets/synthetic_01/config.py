LIEDER_CORPUS_PATH = "datasets/OpenScore-Lieder"
DATASET_PATH = "datasets/synthetic_01"
MSCORE = "musescore/musescore.AppImage"
TESTSET_SCORES_YAML = "testset/test_scores.yaml"
IGNORED_SCORE_IDS = [
    # Do not contain piano part:
    8708253, # https://musescore.com/openscore-lieder-corpus/scores/8708253
    8708688, # https://musescore.com/openscore-lieder-corpus/scores/8708688
    8712405, # https://musescore.com/openscore-lieder-corpus/scores/8712405
    8712648, # https://musescore.com/openscore-lieder-corpus/scores/8712648
    8702982, # https://musescore.com/openscore-lieder-corpus/scores/8702982
    8718660, # https://musescore.com/openscore-lieder-corpus/scores/8718660
    6022950, # https://musescore.com/openscore-lieder-corpus/scores/6022950
    6023075, # https://musescore.com/openscore-lieder-corpus/scores/6023075
    6024601, # https://musescore.com/openscore-lieder-corpus/scores/6024601
    6034442, # https://musescore.com/openscore-lieder-corpus/scores/6034442
    6034473, # https://musescore.com/openscore-lieder-corpus/scores/6034473
    6034767, # https://musescore.com/openscore-lieder-corpus/scores/6034767
    5092551, # https://musescore.com/openscore-lieder-corpus/scores/5092551

    # Has three staves per system for piano
    6005658, # https://musescore.com/openscore-lieder-corpus/scores/6005658

    # Has four voices (on piano) written as four part lines, no pianoform here
    5908953, # https://musescore.com/openscore-lieder-corpus/scores/5908953

    # The piano is two monophonic staves, not one grandstaff
    4982535, # https://musescore.com/openscore-lieder-corpus/scores/4982535

    # Guitar part, one or two staves, complicated -> ignore
    # Also, may lack the grand-staff brace
    6598368, # https://musescore.com/openscore-lieder-corpus/scores/6598368
    6666995, # https://musescore.com/openscore-lieder-corpus/scores/6666995
    6158642, # https://musescore.com/openscore-lieder-corpus/scores/6158642
    6159296, # https://musescore.com/openscore-lieder-corpus/scores/6159296
    6159273, # https://musescore.com/openscore-lieder-corpus/scores/6159273
    6163298, # https://musescore.com/openscore-lieder-corpus/scores/6163298
    6158825, # https://musescore.com/openscore-lieder-corpus/scores/6158825

    # contains piano brace for non-piano parts
    # --> it's hard to crop out the piano part
    6681689, # https://musescore.com/openscore-lieder-corpus/scores/6681689
    6690090, # https://musescore.com/openscore-lieder-corpus/scores/6690090
]
