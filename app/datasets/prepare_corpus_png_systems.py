import os
import glob
import json
from typing import Dict, Any
from .config import LIEDER_CORPUS_PATH
from .crop_system_from_png_page import crop_system_from_png_page


def prepare_corpus_png_systems(
    scores: Dict[int, Dict[str, Any]],
    soft=False
):
    for score_id, score in scores.items():
        score_folder = os.path.join(LIEDER_CORPUS_PATH, "scores", score["path"])
        png_systems_folder = os.path.join(score_folder, "png")

        # skip already converted
        if soft:
            if os.path.isdir(png_systems_folder):
                continue
        
        os.makedirs(png_systems_folder, exist_ok=True)
        
        png_page_glob = os.path.join(glob.escape(score_folder), f"lc{score_id}-*.png")
        for png_page_path in sorted(glob.glob(png_page_glob)):
            basename = os.path.basename(png_page_path)
            page_number_str = basename[len(f"lc{score_id}-"):-len(".png")]
            page_number = int(page_number_str)
            geometry_path = png_page_path.replace(".png", ".geometry.json")

            print("Slicing to PNG:", png_page_path, "...")
            with open(geometry_path) as file:
                page_geometry = json.load(file)
            
            for i, bbox in enumerate(page_geometry["systems"]):
                system_number = i + 1
                crop_system_from_png_page(
                    page_png=png_page_path,
                    bbox=(
                        bbox["left"],
                        bbox["top"],
                        bbox["right"],
                        bbox["bottom"]
                    ),
                    out_system_png=os.path.join(
                        png_systems_folder, f"p{page_number}-s{system_number}.png"
                    ),
                    alpha_to_black_on_white=True
                )
