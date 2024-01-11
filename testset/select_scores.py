import yaml
import random
import csv
from typing import Dict, Any, List


TEST_SCORE_COUNT = 140  # how many scores to take
SEED = 280507783
CORPUS_SCORES_YAML = "../datasets/OpenScore-Lieder/data/scores.yaml"
TEST_SCORES_YAML = "./test_scores.yaml"
IMSLP_FILES_TSV = "./imslp_files.tsv"
with open("../ignored_scores.yaml") as file:
    IGNORED_SCORE_IDS = yaml.safe_load(file)["ignored_score_ids"]


def load_all_scores() -> Dict[str, Dict[str, Any]]:
    with open(CORPUS_SCORES_YAML) as f:
        all_scores = yaml.load(f, Loader=yaml.FullLoader)
    return all_scores


def select_test_scores(
    all_scores: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    all_score_ids = list(all_scores.keys())

    rng = random.Random(SEED)
    rng.shuffle(all_score_ids)

    testset_score_ids = []
    i = 0
    while len(testset_score_ids) < TEST_SCORE_COUNT:
        id = all_score_ids[i]
        if id not in IGNORED_SCORE_IDS:
            testset_score_ids.append(id)
        i += 1

    testset_scores = {
        id: score
        for id, score in all_scores.items()
        if id in set(testset_score_ids)
    }

    return testset_scores


def save_test_scores(test_scores: Dict[str, Dict[str, Any]]):
    sorted_scores = dict(sorted(
        test_scores.items(),
        key=lambda item: item[1]["path"]
    ))
    assert len(sorted_scores) == TEST_SCORE_COUNT
    with open(TEST_SCORES_YAML, "w") as f:
        yaml.dump(sorted_scores, f, allow_unicode=True, sort_keys=False)


def extract_imslp_files(
    test_scores: Dict[str, Dict[str, Any]]
) -> List[Dict[str, str]]:
    imslp_ids = set(score["imslp"] for score in test_scores.values())
    records = [{
        "id": id,
        "url": "https://imslp.org/wiki/Special:ReverseLookup/" + id[1:]
    } for id in imslp_ids]
    records.sort(key=lambda record: int(record["id"][1:]))
    return records


def save_imslp_files(imslp_files_records: List[Dict[str, str]]):
    with open(IMSLP_FILES_TSV, "w", newline="") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "id",
            "url"
        ])
        for record in imslp_files_records:
            writer.writerow([
                record["id"],
                record["url"]
            ])


def main():
    all_scores = load_all_scores()
    test_scores = select_test_scores(all_scores)
    save_test_scores(test_scores)
    imslp_files_records = extract_imslp_files(test_scores)
    save_imslp_files(imslp_files_records)


if __name__ == '__main__':
    main()
