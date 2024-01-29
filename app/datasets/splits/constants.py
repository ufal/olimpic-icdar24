import yaml
import os


SEED = 280507783

with open(os.path.join(os.path.dirname(__file__), "globally_ignored_scores.yaml")) as file:
    GLOBALLY_IGNORED_SCORES = yaml.safe_load(file)

with open(os.path.join(os.path.dirname(__file__), "annotation_problematic_scores.yaml")) as file:
    ANNOTATION_PROBLEMATIC_SCORES = yaml.safe_load(file)
