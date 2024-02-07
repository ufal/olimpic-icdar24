import yaml
import os
import io
import glob
import cv2
from .detect_systems_in_svg import detect_systems_in_svg
from ..musescore_corpus_conversion import musescore_corpus_conversion
from ..config import SCANNED_DATASET_PATH, LIEDER_CORPUS_PATH


WORKBENCH_RECT_COLOR = "#eb5454"


def load_workbench(score_id: int):
    # get all the scores metadata
    with open(os.path.join(LIEDER_CORPUS_PATH, "data", "scores.yaml")) as file:
        all_scores = yaml.safe_load(file)
    
    # check the workbench file does not exist
    workbench_file = os.path.join(SCANNED_DATASET_PATH, "workbench.svg")
    if os.path.isfile(workbench_file):
        print("[ERROR] Workbench file already exists.")
        return

    print("Loading score", score_id, ":")
    for key, value in all_scores[score_id].items():
        print(str(key) + ":", value)
    print()

    imslp_id = all_scores[score_id]["imslp"][1:]

    open_imslp_pdf(imslp_id)
    
    start_page = int(input("Enter the starting page: "))

    musescore_corpus_conversion(
        {score_id: all_scores[score_id]},
        format="svg",
        soft=True
    )

    svg_pages = detect_systems_in_svg(score_id)
    imslp_pages = get_imslp_pages(imslp_id, start_page, len(svg_pages))

    with open(workbench_file, "w") as file:
        create_inkscape_file(svg_pages, imslp_pages, score_id, imslp_id, file)


def open_imslp_pdf(imslp_id: str):
    pattern = os.path.join(SCANNED_DATASET_PATH, "imslp_pdfs", "IMSLP" + imslp_id + "*.pdf")
    paths = glob.glob(pattern)
    path = paths[0]

    # open the PDF using the "evince" ubuntu PDF viewer
    os.system(f"evince \"{path}\"")


def get_imslp_pages(imslp_id: str, start_page: int, page_count: int):
    imslp_pages = []
    
    for i in range(page_count):
        page_number = i + start_page
        
        path_pattern = os.path.join(
            SCANNED_DATASET_PATH, "imslp_pngs", "IMSLP" + imslp_id,
            "IMSLP" + imslp_id + "-" + str(page_number).zfill(3) + "-*.png"
        )
        paths = list(sorted(glob.glob(path_pattern)))
        path = paths[0]

        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        height, width = img.shape
        
        imslp_pages.append({
            "path": os.path.realpath(path),
            "width": width,
            "height": height,
            "imslp_id": imslp_id,
            "page_number": page_number
        })

    return imslp_pages


def create_inkscape_file(svg_pages, imslp_pages, score_id, imslp_id, file: io.FileIO):
    PAGE_HEIGHT = 297
    SPACING = 10
    CORPUS_X = 0
    imslp_x = 0

    file.write(f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg
        score-id="{score_id}"
        imslp-id="{imslp_id}"
        imslp-start-page="{imslp_pages[0]["page_number"]}"
        width="793.70081"
        height="1122.5197"
        viewBox="0 0 210 297"
        version="1.1"
        id="svg5"
        inkscape:version="1.1 (1:1.1+202106031931+af4d65493e)"
        sodipodi:docname="workbench.svg"
        xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
        xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:svg="http://www.w3.org/2000/svg">
        <sodipodi:namedview
            id="namedview7"
            pagecolor="#505050"
            bordercolor="#ffffff"
            borderopacity="1"
            inkscape:pageshadow="0"
            inkscape:pageopacity="0"
            inkscape:pagecheckerboard="1"
            inkscape:document-units="mm"
            showgrid="false"
            units="px"
            inkscape:zoom="0.13716686"
            inkscape:cx="583.23125"
            inkscape:cy="3138.5132"
            inkscape:window-width="1920"
            inkscape:window-height="1030"
            inkscape:window-x="0"
            inkscape:window-y="24"
            inkscape:window-maximized="1"
            inkscape:current-layer="layer2" />
        <defs
            id="defs2" />
        <g
            inkscape:label="Images"
            inkscape:groupmode="layer"
            id="layer1"
            sodipodi:insensitive="true">
    """)

    # print OS lieder corpus SVGs
    for pi, svg_page in enumerate(svg_pages):
        path = svg_page["path"]
        score_id = svg_page["score_id"]
        page_number = svg_page["page_number"]
        ratio = PAGE_HEIGHT / svg_page["page_height"]
        height = svg_page["page_height"] * ratio
        width = svg_page["page_width"] * ratio
        px = CORPUS_X
        py = pi * (PAGE_HEIGHT + SPACING)
        imslp_x = max(imslp_x, px + width + SPACING)
        file.write(f"""
        <rect
            style="fill:#ffffff;fill-opacity:1.0;"
            id="paper-white-lc{score_id}-p{page_number}"
            width="{width}"
            height="{height}"
            x="{px}"
            y="{py}" />
        """)
        file.write(f"""
        <image
            width="{width}"
            height="{height}"
            preserveAspectRatio="none"
            xlink:href="{path}"
            id="lc{score_id}-p{page_number}"
            x="{px}"
            y="{py}" />
        """)
    
    # print IMSLP PNGs
    for pi, imslp_page in enumerate(imslp_pages):
        path = imslp_page["path"]
        imslp_id = imslp_page["imslp_id"]
        page_number = imslp_page["page_number"]
        ratio = PAGE_HEIGHT / imslp_page["height"]
        height = imslp_page["height"] * ratio
        width = imslp_page["width"] * ratio
        px = imslp_x
        py = pi * (PAGE_HEIGHT + SPACING)
        file.write(f"""
        <image
            imslp-image="true"
            imslp-page-number="{page_number}"
            imslp-width="{imslp_page['width']}"
            imslp-height="{imslp_page['height']}"
            width="{width}"
            height="{height}"
            preserveAspectRatio="none"
            xlink:href="{path}"
            id="IMSLP{imslp_id}-p{page_number}"
            x="{px}"
            y="{py}" />
        """)

    # from images to annotations
    file.write("""
    </g>
    <g
        inkscape:groupmode="layer"
        id="layer2"
        inkscape:label="Annotations"
        style="display:inline">
    """)

    # print OS lieder system bounding boxes
    for pi, svg_page in enumerate(svg_pages):
        path = svg_page["path"]
        score_id = svg_page["score_id"]
        page_number = svg_page["page_number"]
        ratio = PAGE_HEIGHT / svg_page["page_height"]
        height = svg_page["page_height"] * ratio
        width = svg_page["page_width"] * ratio
        px = CORPUS_X
        py = pi * (PAGE_HEIGHT + SPACING)
        for si, system in enumerate(svg_page["systems"]):
            sx = system["left"] * ratio
            sy = system["top"] * ratio
            sw = (system["right"] - system["left"]) * ratio
            sh = (system["bottom"] - system["top"]) * ratio
            file.write(f"""
            <rect
                style="fill:{WORKBENCH_RECT_COLOR};fill-opacity:0.366049;"
                id="lc{score_id}-p{page_number}-s{si + 1}"
                width="{sw}"
                height="{sh}"
                x="{px + sx}"
                y="{py + sy}" />
            """)

    # footer
    file.write("""
      </g>
    </svg>
    """)
