from typing import Dict, Any, List
import os
import glob


def build_dataset_index(
    scores: Dict[int, Dict[str, Any]],
    slice_name: str,
    dataset_path: str,
    from_sample_format="png"
):
    actual_sample_bases: List[str] = []

    for score_id in scores.keys():
        pattern = os.path.join(
            dataset_path, "samples", str(score_id),
            f"*.{from_sample_format}"
        )
        bases = [
            p[:-len(f".{from_sample_format}")]
            for p in glob.glob(pattern)
        ]
        
        for base in bases:
            actual_sample_bases.append(
                os.path.relpath(base, dataset_path)
            )
    
    # check uniqueness
    assert len(actual_sample_bases) == len(set(actual_sample_bases))

    # write index
    with open(os.path.join(dataset_path, f"samples.{slice_name}.txt"), "w") as file:
        for base in actual_sample_bases:
            file.write(base + "\n")
