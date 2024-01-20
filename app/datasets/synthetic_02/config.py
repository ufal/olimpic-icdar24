import yaml


LIEDER_CORPUS_PATH = "datasets/OpenScore-Lieder"
DATASET_PATH = "datasets/synthetic_02"
MSCORE = "musescore/musescore.AppImage"
TESTSET_SCORES_YAML = "testset/test_scores.yaml"

with open("ignored_scores.yaml") as file:
    IGNORED_SCORE_IDS = yaml.safe_load(file)["ignored_score_ids"]
