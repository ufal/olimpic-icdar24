import yaml

from .write_scores import write_scores
from .write_sets import write_sets
from .print_pdfs import print_pdfs
from .generate_test_partition import generate_test_partition
from .generate_dev_partition import generate_dev_partition
from .print_scores import print_scores


def generate():
    with open("datasets/OpenScore-Lieder/data/scores.yaml") as file:
        all_scores = yaml.safe_load(file)
    with open("datasets/OpenScore-Lieder/data/sets.yaml") as file:
        all_sets = yaml.safe_load(file)
    
    print("##################")
    print("# Test partition #")
    print("##################")
    print()

    print("Scores")
    print("------")
    test_score_ids = generate_test_partition(all_scores, all_sets)
    print_scores(all_scores, test_score_ids)
    print()

    test_sets_ids = set(
        all_scores[score_id]["set_id"] for score_id in test_score_ids
    )

    write_scores(all_scores, test_score_ids, "data/test_scores.yaml")
    write_sets(all_sets, test_sets_ids, "data/test_sets.yaml")

    print("IMSLP PDFs")
    print("----------")
    print_pdfs(all_scores, test_score_ids)
    print()

    print("#################")
    print("# Dev partition #")
    print("#################")
    print()

    print("Scores")
    print("------")
    dev_score_ids = generate_dev_partition(all_scores, test_sets_ids)
    print_scores(all_scores, dev_score_ids)
    print()

    write_scores(all_scores, dev_score_ids, "data/dev_scores.yaml")

    print("IMSLP PDFs")
    print("----------")
    print_pdfs(all_scores, dev_score_ids)
    print()
