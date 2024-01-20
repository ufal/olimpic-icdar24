import os
import yaml
from .config import *
from .check_system_correspondence import check_system_correspondence
from .build_test_train_indexes import build_test_train_indexes


def finalize():
    # load and filter corpus scores
    with open(os.path.join(LIEDER_CORPUS_PATH, "data/scores.yaml")) as f:
        corpus_scores = yaml.load(f, Loader=yaml.FullLoader)
    for score_id in IGNORED_SCORE_IDS:
        del corpus_scores[score_id]
    
    with open(TESTSET_SCORES_YAML) as f:
        testset_scores = yaml.load(f, Loader=yaml.FullLoader)

    score_ids = list(corpus_scores.keys())
    testset_ids = list(testset_scores.keys())
    
    # check that LMX and PNG files are paired correctly
    check_system_correspondence(score_ids=score_ids, flavor="extended")
    check_system_correspondence(score_ids=score_ids, flavor="core")

    # build indexes
    build_test_train_indexes(
        score_ids=score_ids,
        testset_ids=testset_ids
    )

    # create vocabulary file
    vocabulary_file_path = os.path.join(DATASET_PATH, "vocabulary.txt")
    with open(vocabulary_file_path, "w") as file:
        from ...linearization.vocabulary import ALL_TOKENS
        print("\n".join(ALL_TOKENS), file=file)

    # remove unnecessary files
    assert os.system(
        f"rm {DATASET_PATH}/conversion_*.json"
    ) == 0
