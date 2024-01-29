import yaml
import os


def write_stats(stats, file: str):
    with open(os.path.join(os.path.dirname(__file__), file), "w") as f:
        yaml.dump(stats, f, allow_unicode=True, sort_keys=False)