import re
from svgelements import *


def _svg_path_to_signature(d: str):
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


def find_systems_in_svg_page(
    svg_path: str,
    bracket_grow=1.1, # multiplier
):
    with open(svg_path) as file:
        svg_file: SVG = SVG.parse(file, reify=True)
    
    # vertical pixel ranges (from-to) for system stafflines
    system_ranges = []
    for element in svg_file.elements():
        if element.values.get("class") == "Bracket":
            signature = _svg_path_to_signature(
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
            start -= height * (bracket_grow - 1) / 2
            stop += height * (bracket_grow - 1) / 2
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
    
    return {
        "page_width": int(svg_file.width),
        "page_height": int(svg_file.height),
        "systems": [
            {
                "left": int(x1),
                "top": int(y1),
                "right": int(x2),
                "bottom": int(y2)
            }
            for x1, y1, x2, y2 in system_bboxes
        ],
    }
