import os
import glob
from typing import Iterable
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
    train_samples, train_scores = build_index(trainset_ids, "train.tsv")
    test_samples, test_scores = build_index(testset_ids, "test.tsv")

    # save dataset sizes
    with open(os.path.join(DATASET_PATH, "statistics.yaml"), "w") as file:
        print("train_set_samples:", train_samples, file=file)
        print("train_set_target_scores:", len(trainset_ids), file=file)
        print("train_set_actual_scores:", train_scores, file=file)

        print("test_set_samples:", test_samples, file=file)
        print("test_set_target_scores:", len(testset_ids), file=file)
        print("test_set_actual_scores:", test_scores, file=file)


def build_index(score_ids: Iterable[int], filename: str) -> int:
    sample_count = 0
    score_count = 0
    with open(os.path.join(DATASET_PATH, filename), "w") as file:
        for id in score_ids:
            pattern = os.path.join(DATASET_PATH, "samples", str(id), "*.msq")
            bases = [p.replace(".msq", "") for p in glob.glob(pattern)]
            
            if len(bases) > 0:
                score_count += 1

            for base in bases:
                png_path = base + ".png"
                msq_path = base + ".msq"
                assert os.path.isfile(png_path)
                assert os.path.isfile(msq_path)
                
                # relativize to the dataset directory
                png_path = os.path.relpath(png_path, DATASET_PATH)
                msq_path = os.path.relpath(msq_path, DATASET_PATH)
                print(
                    f"{png_path}\t{msq_path}",
                    file=file
                )
                sample_count += 1
    
    return (sample_count, score_count)
