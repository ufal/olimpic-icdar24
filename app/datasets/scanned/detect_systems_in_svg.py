import os
import glob
from ..config import LIEDER_CORPUS_PATH
from ..find_systems_in_svg_page import find_systems_in_svg_page


def detect_systems_in_svg(score_id: int):
    svg_pages = []
    
    pattern = os.path.join(LIEDER_CORPUS_PATH, "scores", "**", f"lc{score_id}-*.svg")
    for svg_path in sorted(glob.glob(pattern, recursive=True)):
        basename = os.path.basename(svg_path)
        page_number = int(basename[len(str(score_id))+3:-len(".svg")])
        
        geometry = find_systems_in_svg_page(svg_path)
        geometry["path"] = os.path.realpath(svg_path)
        geometry["score_id"] = score_id
        geometry["page_number"] = page_number

        svg_pages.append(geometry)
    
    assert len(svg_pages) > 0

    return svg_pages
