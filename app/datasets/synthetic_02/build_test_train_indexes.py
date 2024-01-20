import os
import glob
from typing import Iterable, List
from .config import *


def build_test_train_indexes(
    score_ids: Iterable[int],
    testset_ids: Iterable[int]
):
    # first, check that the testset does not contain any excluded IDs
    # (that it's a clean subset)
    for id in testset_ids:
        if id not in score_ids:
            print("TESTSET SCORE WAS NOT PROCESSED:", id)
    
    # get train IDs by filtering out the test ones
    trainset_ids = [id for id in score_ids if id not in testset_ids]

    # build the indices
    train_samples, train_scores = build_index(trainset_ids, "train")
    test_samples, test_scores = build_index(testset_ids, "test")

    # save dataset sizes
    with open(os.path.join(DATASET_PATH, "statistics.yaml"), "w") as file:
        print("train_set_samples:", train_samples, file=file)
        print("train_set_target_scores:", len(trainset_ids), file=file)
        print("train_set_actual_scores:", train_scores, file=file)

        print("test_set_samples:", test_samples, file=file)
        print("test_set_target_scores:", len(testset_ids), file=file)
        print("test_set_actual_scores:", test_scores, file=file)


def build_index(score_ids: Iterable[int], index_name: str) -> int:
    actual_score_ids: List[str] = []
    actual_sample_bases: List[str] = []

    for id in score_ids:
        pattern = os.path.join(DATASET_PATH, "samples", str(id), "*.png")
        bases = [p.replace(".png", "") for p in glob.glob(pattern)]
        
        if len(bases) > 0:
            actual_score_ids.append(str(id))

        for base in bases:
            actual_sample_bases.append(
                os.path.relpath(base, DATASET_PATH)
            )
    
    # check uniqueness
    assert len(actual_score_ids) == len(set(actual_score_ids))
    assert len(actual_sample_bases) == len(set(actual_sample_bases))

    # write scores index
    with open(os.path.join(DATASET_PATH, f"scores.{index_name}.txt"), "w") as file:
        for id in actual_score_ids:
            file.write(id + "\n")

    # write samples index
    with open(os.path.join(DATASET_PATH, f"samples.{index_name}.txt"), "w") as file:
        for base in actual_sample_bases:
            file.write(base + "\n")

    return (len(actual_sample_bases), len(actual_score_ids))
