import yaml
from typing import Set

from .constants import *
from .write_scores import write_scores
from .write_sets import write_sets
from .write_stats import write_stats
from .generate_test_partition import generate_test_partition
from .generate_dev_partition import generate_dev_partition
from .generate_train_partition import generate_train_partition


def generate():
    print("Loading the corpus...")
    with open("datasets/OpenScore-Lieder/data/scores.yaml") as file:
        all_scores = yaml.safe_load(file)
    with open("datasets/OpenScore-Lieder/data/sets.yaml") as file:
        all_sets = yaml.safe_load(file)
    
    # == TEST ==

    print("Generating the test partition...")
    test_scores_ids: Set[int] = generate_test_partition(
        all_scores,
        all_sets
    )
    test_sets_ids: Set[int] = set(
        all_scores[score_id]["set_id"] for score_id in test_scores_ids
    )
    write_scores(all_scores, test_scores_ids, "data/test_scores.yaml")
    write_sets(all_sets, test_sets_ids, "data/test_sets.yaml")

    # == DEV ==

    print("Generating the dev partition...")
    dev_scores_ids: Set[int] = generate_dev_partition(
        all_scores,
        test_sets_ids
    )
    write_scores(all_scores, dev_scores_ids, "data/dev_scores.yaml")

    # == TRAIN ==

    print("Generating the train partition...")
    train_scores_ids: Set[int] = generate_train_partition(
        all_scores,
        test_sets_ids,
        dev_scores_ids
    )
    write_scores(all_scores, train_scores_ids, "data/train_scores.yaml")

    # == STATS ==

    print("Computing statistics...")
    write_stats({
        "train": {
            "scores": len(train_scores_ids)
        },
        "dev": {
            "scores": len(dev_scores_ids)
        },
        "test": {
            "scores": len(test_scores_ids),
            "sets": len(test_sets_ids)
        },
        "corpus": {
            "scores": len(all_scores),
            "sets": len(all_sets)
        },
        "globally_ignored_scores": len(GLOBALLY_IGNORED_SCORES),
        "annotation_problematic_scores": len(ANNOTATION_PROBLEMATIC_SCORES)
    }, "data/stats.yaml")

    print("Done.")
