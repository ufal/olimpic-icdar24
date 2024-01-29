from typing import Set
import yaml
import os


def write_sets(all_sets, sets_ids: Set[int], file: str):
    sorted_sets = dict(sorted(
        ((set_id, all_sets[set_id]) for set_id in sets_ids),
        key=lambda item: item[1]["path"]
    ))
    with open(os.path.join(os.path.dirname(__file__), file), "w") as f:
        yaml.dump(sorted_sets, f, allow_unicode=True, sort_keys=False)