import os
import glob
import json
import cv2
import re
from typing import Iterable
from svgelements import *
from .config import *


def slice_system_pngs(score_ids: Iterable[int]):
    for score_id in score_ids:

        pattern = os.path.join(DATASET_PATH, "svg", f"{score_id}-*.svg")
        for svg_path in glob.glob(pattern):
            basename = os.path.basename(svg_path)
            page_number = int(basename[len(str(score_id))+1:-len(".svg")])
            png_path = svg_path.replace("svg", "png")
            
            print("Slicing to PNG:", svg_path, "...")
            system_cropboxes, page_geometry = find_systems_in_svg(svg_path)

            page_geometry_filename = os.path.join(
                DATASET_PATH, "samples", str(score_id),
                f"p{page_number}_geometry.json"
            )
            with open(page_geometry_filename, "w") as file:
                json.dump(page_geometry, file, indent=2)
            
            img = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
            img = 255 - img[:, :, 3] # alpha becomes black on white

            for i, (x1, y1, x2, y2) in enumerate(system_cropboxes):
                system_number = i + 1
                system_png_path = os.path.join(
                    DATASET_PATH, "samples", str(score_id),
                    f"p{page_number}-s{system_number}.png"
                )
                os.makedirs(os.path.dirname(system_png_path), exist_ok=True)
                system_img = img[y1:y2,x1:x2]
                cv2.imwrite(system_png_path, system_img)


def svg_path_to_signature(d: str):
    """Replaces numbers with underscores, 
    useful for notation object type matching"""
    return re.sub(r"-?\d+(\.\d+)?", "_", d)


PIANO_BRACKET_SIGNATURES = [
    "M_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_",

    "M_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_"
]
NON_PIANO_BRACKET_SIGNATURES = [
    # ensamble bracket body has "points" instead of "d", so "d" is an empty string
    "",
    
    # ensamble bracket ends have this signature (top end and bottom end)
    "M_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_",
    "M_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_",
    # bracket ends, another variant
    "M_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ C_,_ _,_ _,_ L_,_ L_,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_",
    "M_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_ L_,_ L_,_ L_,_ C_,_ _,_ _,_ L_,_ C_,_ _,_ _,_ C_,_ _,_ _,_ C_,_ _,_ _,_",
]


def find_systems_in_svg(
    svg_path: str,
    bracket_grow=1.1, # multiplier
    vertical_margin=0.5, # in the multiples of system height
    horizontal_margin=0.5 # in the multiples of system height
):
    with open(svg_path) as file:
        svg_file: SVG = SVG.parse(file, reify=True)
    
    # vertical pixel ranges (from-to) for system stafflines
    system_ranges = []
    for element in svg_file.elements():
        if element.values.get("class") == "Bracket":
            signature = svg_path_to_signature(
                element.values["attributes"].get("d", "")
            )
            if signature in NON_PIANO_BRACKET_SIGNATURES:
                continue
            if signature not in PIANO_BRACKET_SIGNATURES:
                print("UNKNOWN BRACKET:", element.values.get("d", ""))
                print(signature)
                continue

            _, start, _, stop = element.bbox(with_stroke=True)
            height = stop - start
            start -= height * (1 - bracket_grow) / 2
            stop += height * (1 - bracket_grow) / 2
            system_ranges.append((start, stop))
    system_ranges.sort(key=lambda range: range[0])
    
    # check the number is reasonable (these actually occur in the corpus)
    assert len(system_ranges) in [0, 1, 2, 3, 4, 5, 6]
    
    # sort stafflines into system bins
    system_stafflines = [[] for _ in system_ranges]
    for element in svg_file.elements():
        if element.values.get("class") == "StaffLines":
            _, y, _, _ = element.bbox()
            for i, (start, stop) in enumerate(system_ranges):
                if start <= y and y <= stop:
                    system_stafflines[i].append(element)
    
    # get system bounding boxes (tight)
    system_bboxes = [
        Group.union_bbox(stafflines)
        for stafflines in system_stafflines
    ]

    # get system crop boxes
    system_cropboxes = []
    for x1, y1, x2, y2 in system_bboxes:
        height = y2 - y1
        # grow by margin
        x1 -= horizontal_margin * height
        x2 += horizontal_margin * height
        y1 -= vertical_margin * height
        y2 += vertical_margin * height
        # hit page border
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, svg_file.width - 1)
        y2 = min(y2, svg_file.height - 1)
        # round to pixel
        system_cropboxes.append((
            int(x1), int(y1), int(x2), int(y2)
        ))
    
    page_geometry = {
        "page_width": svg_file.width,
        "page_height": svg_file.height,
        "systems": [
            {
                "left": int(x1),
                "top": int(y1),
                "right": int(x2),
                "bottom": int(y2)
            }
            for x1, y1, x2, y2 in system_bboxes
        ],
        "cropboxes": [
            {
                "left": int(x1),
                "top": int(y1),
                "right": int(x2),
                "bottom": int(y2)
            }
            for x1, y1, x2, y2 in system_cropboxes
        ]
    }

    return system_cropboxes, page_geometry
