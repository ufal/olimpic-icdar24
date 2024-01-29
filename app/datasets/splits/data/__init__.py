import yaml
import os


with open(os.path.join(os.path.dirname(__file__), "dev_scores.yaml")) as file:
    DEV_SCORES = yaml.safe_load(file)

with open(os.path.join(os.path.dirname(__file__), "test_scores.yaml")) as file:
    TEST_SCORES = yaml.safe_load(file)

with open(os.path.join(os.path.dirname(__file__), "test_sets.yaml")) as file:
    TEST_SETS = yaml.safe_load(file)

with open(os.path.join(os.path.dirname(__file__), "train_scores.yaml")) as file:
    TRAIN_SCORES = yaml.safe_load(file)
