import os
import glob
import json
import cv2
from typing import Dict, Any
from .config import LIEDER_CORPUS_PATH
from .find_systems_in_svg_page import find_systems_in_svg_page


def prepare_corpus_page_geometries(scores: Dict[int, Dict[str, Any]]):
    for score_id, score in scores.items():
        score_folder = os.path.join(LIEDER_CORPUS_PATH, "scores", score["path"])
        
        svg_glob = os.path.join(glob.escape(score_folder), f"lc{score_id}-*.svg")
        for svg_path in sorted(glob.glob(svg_glob)):
            basename = os.path.basename(svg_path)
            page_number_str = basename[len(f"lc{score_id}-"):-len(".svg")]

            print("Detecting page geometry:", svg_path, "...")
            page_geometry = find_systems_in_svg_page(svg_path)

            page_geometry_filename = os.path.join(
                score_folder,
                f"lc{score_id}-{page_number_str}.geometry.json"
            )
            with open(page_geometry_filename, "w") as file:
                json.dump(page_geometry, file, indent=2)
