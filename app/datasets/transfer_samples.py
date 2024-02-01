from typing import Dict, Any
import os
from .config import LIEDER_CORPUS_PATH
import shutil
import glob


def transfer_samples(
    scores: Dict[int, Dict[str, Any]],
    corpus_glob: str,
    dataset_folder: str
):
    """Transfer sample files from corpus folder to dataset folder"""
    
    print("Transferring samples", corpus_glob, "...")
    
    for score_id, score in scores.items():
        score_folder = os.path.join(LIEDER_CORPUS_PATH, "scores", score["path"])
        sample_folder = os.path.join(dataset_folder, "samples", str(score_id))

        os.makedirs(sample_folder, exist_ok=True)

        samples = list(sorted(glob.glob(
            os.path.join(glob.escape(score_folder), corpus_glob),
            recursive=True
        )))

        for sample in samples:
            sample_name = os.path.basename(sample)
            target_path = os.path.join(sample_folder, sample_name)

            shutil.copyfile(sample, target_path)
