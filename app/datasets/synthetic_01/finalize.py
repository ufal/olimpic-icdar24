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
    
    # check that MSQ and PNG files are paired correctly
    check_system_correspondence(score_ids=score_ids)

    # build sample indexes
    build_test_train_indexes(
        score_ids=score_ids,
        testset_ids=testset_ids
    )

    # merge vocabularies
    assert os.system(
        f"sort -u {DATASET_PATH}/vocabulary_*.txt > {DATASET_PATH}/vocabulary.txt"
    ) == 0

    # merge errors
    assert os.system(
        f"cat {DATASET_PATH}/msq_errors_*.txt > {DATASET_PATH}/msq_errors.txt"
    ) == 0

    # remove unnecessary files
    assert os.system(
        f"rm {DATASET_PATH}/vocabulary_*.txt"
    ) == 0
    assert os.system(
        f"rm {DATASET_PATH}/msq_errors_*.txt"
    ) == 0
    assert os.system(
        f"rm {DATASET_PATH}/conversion_*.json"
    ) == 0
