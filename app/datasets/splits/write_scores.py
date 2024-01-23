from typing import List
import yaml
import os


def write_scores(all_scores, score_ids: List[int], file: str):
    sorted_scores = dict(sorted(
        ((score_id, all_scores[score_id]) for score_id in score_ids),
        key=lambda item: item[1]["path"]
    ))
    with open(os.path.join(os.path.dirname(__file__), file), "w") as f:
        yaml.dump(sorted_scores, f, allow_unicode=True, sort_keys=False)