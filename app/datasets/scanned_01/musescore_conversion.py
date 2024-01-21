from typing import Dict, Any
import os
import json
from .config import *


def musescore_conversion(
    scores: Dict[int, Dict[str, Any]],
    formats=["mxl", "svg", "png"]
):
    """Executes MuseScore batch conversion"""

    if len(formats) == 0:
        return

    # create folders
    for format in formats:
        os.makedirs(os.path.join(DATASET_PATH, format), exist_ok=True)

    # create the conversion json file
    conversion_filename = os.path.join(
        DATASET_PATH,
        f"conversion.json"
    )

    conversion = []
    for format in formats:
        for score_id, score in scores.items():
            out_path = os.path.join(DATASET_PATH, format, f"{score_id}.{format}")

            # skip already exported files
            if os.path.isfile(out_path):
                continue
            if os.path.isfile(out_path.replace(f".{format}", f"-1.{format}")):
                continue
            if os.path.isfile(out_path.replace(f".{format}", f"-01.{format}")):
                continue

            conversion.append({
                "in": os.path.join(
                    LIEDER_CORPUS_PATH, "scores", score["path"], f"lc{score_id}.mscx"
                ),
                "out": out_path
            })
    
    if len(conversion) == 0:
        return
    
    with open(conversion_filename, "w") as file:
        json.dump(conversion, file)
    
    # run musescore
    assert os.system(
        f"{MSCORE} -j {conversion_filename}"
    ) == 0
