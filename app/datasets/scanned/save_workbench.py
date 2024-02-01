import os
import yaml
from svgelements import *
from .detect_systems_in_svg import detect_systems_in_svg
from ..config import SCANNED_DATASET_PATH


WORKBENCH_RECT_COLOR = "#eb5454"


def save_workbench():
    workbench_file = os.path.join(SCANNED_DATASET_PATH, "workbench.svg")
    
    with open(workbench_file) as file:
        svg_file: SVG = SVG.parse(file, reify=True)
    
    score_id: int = None
    imslp_id: str = None
    imslp_start_page: int = None
    annotation_bboxes = []
    imslp_pages = {}
    
    for element in svg_file.elements():
        if type(element) is SVG:
            score_id = int(element.values["score-id"])
            imslp_start_page = int(element.values["imslp-start-page"])
            imslp_id = str(element.values["imslp-id"])
        elif type(element) is Image:
            if element.values.get("imslp-image") == "true":
                page_number = int(element.values.get("imslp-page-number"))
                page = imslp_pages.get(page_number, {})
                page["image"] = element.values.get("{http://www.w3.org/1999/xlink}href")
                x = float(element.values.get("x"))
                y = float(element.values.get("y"))
                width = float(element.values.get("width"))
                height = float(element.values.get("height"))
                page["bbox"] = (
                    x, y, x + width, y + height
                )
                page["width"] = int(element.values.get("imslp-width"))
                page["height"] = int(element.values.get("imslp-height"))
                imslp_pages[page_number] = page
        elif type(element) is Rect:
            if not str(element.fill).startswith(WORKBENCH_RECT_COLOR):
                continue
            x = float(element.values.get("x"))
            y = float(element.values.get("y"))
            width = float(element.values.get("width"))
            height = float(element.values.get("height"))
            annotation_bboxes.append((
                x, y, x + width, y + height
            ))
    
    print("Parsed score id:", score_id)
    
    # create the imslp system bboxes values to overwrite
    for page_number in sorted(imslp_pages.keys()):
        page = imslp_pages[page_number]

        annotations = [
            bbox for bbox in annotation_bboxes
            if bbox_inside_bbox(bbox, page["bbox"])
        ]
        annotations.sort(key=lambda bbox: bbox[1]) # y1

        px1, py1, px2, py2 = page["bbox"]
        xratio = page["width"] / (px2 - px1)
        yratio = page["height"] / (py2 - py1)
        page["systems"] = [
            {
                "boundingBox": {
                    "left": int((x1 - px1) * xratio),
                    "top": int((y1 - py1) * yratio),
                    "width": int((x2 - x1) * xratio),
                    "height": int((y2 - y1) * yratio),
                }
            }
            for x1, y1, x2, y2 in annotations
        ]
        page["image"] = os.path.relpath(
            page["image"],
            os.path.join(SCANNED_DATASET_PATH, "imslp_pngs")
        )

        # remove unnecessary values
        del page["bbox"]

    # create the system mapping file
    corpus_to_imslp = {}
    svg_pages = detect_systems_in_svg(score_id)
    for svg_page in svg_pages:
        svg_page_number = svg_page["page_number"]
        imslp_page_number = imslp_start_page + (svg_page_number - 1)
        for si, _ in enumerate(svg_page["systems"]):
            system_number = si + 1

            # check that an imslp system bbox is defined
            assert imslp_page_number in imslp_pages
            page = imslp_pages[imslp_page_number]
            assert (system_number - 1) < len(page["systems"])

            corpus_to_imslp[f"{score_id}/p{svg_page_number}-s{system_number}"] = {
                "imslpDocument": "#" + imslp_id,
                "imslpPage": imslp_page_number,
                "imslpSystem": system_number
            }

    # write the results
    systems_file_path = os.path.join(SCANNED_DATASET_PATH, "imslp_systems", "IMSLP" + imslp_id + ".yaml")
    print("Writing:", systems_file_path)
    if os.path.exists(systems_file_path):
        with open(systems_file_path) as file:
            contents = yaml.safe_load(file)
    else:
        contents = {"pages": {}}
    for page_number, page in imslp_pages.items():
        contents["pages"][page_number] = page
    with open(systems_file_path, "w") as file:
        yaml.safe_dump(contents, file, sort_keys=True)

    map_file_path = os.path.join(SCANNED_DATASET_PATH, "corpus_to_imslp", str(score_id) + ".yaml")
    print("Writing:", map_file_path)
    with open(map_file_path, "w") as file:
        contents = corpus_to_imslp
        yaml.safe_dump(contents, file, sort_keys=True)

    # remove the workbench file
    print("Removing the workbench file.")
    assert os.system(f"rm {workbench_file}") == 0
    print("Done.")
    

def bbox_inside_bbox(a, b) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return (
        bx1 < ax1 and ax2 < bx2 and
        by1 < ay1 and ay2 < by2
    )