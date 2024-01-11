import os
from .config import *


def clear():
    # clear the dataset folder to get a fresh start
    assert os.system(f"rm -rf {DATASET_PATH}") == 0
